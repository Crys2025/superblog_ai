import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def extract_probe_data(url: str) -> dict:
    output = {
        "probe_title": "",
        "intro": "",
        "full_text": "",
        "sponsors": [],
        "images": [],
        "keywords": [],
        "requirements": [],
        "jury_criteria": [],
        "bonuses": [],
        "deadline": "",
        "theme_summary": "",
    }

    # -------------------- FETCH PAGE --------------------
    try:
        response = requests.get(url, timeout=25)
        response.raise_for_status()
    except Exception as e:
        return {"error": f"Eroare la încărcarea linkului: {e}"}

    soup = BeautifulSoup(response.text, "html.parser")

    # -------------------- TITLU --------------------
    title_tag = (
        soup.find("h1", class_="entry-title")
        or soup.find("h1", class_="tdb-title-text")
        or soup.find("h1")
    )
    if title_tag:
        output["probe_title"] = title_tag.get_text(strip=True)

    # -------------------- DETECT CONTENT BLOCK --------------------
    POSSIBLE_CONTENT_SELECTORS = [
        "div.entry-content",
        "div.td-post-content",
        "div.tdb-block-inner",
        "article div.td-post-content",
        "article"
    ]

    content = None
    for selector in POSSIBLE_CONTENT_SELECTORS:
        c = soup.select_one(selector)
        if c:
            content = c
            break

    if not content:
        return {"error": "Nu am putut identifica conținutul principal."}

    # curățare
    for tag in content.find_all(["script", "style", "header", "footer", "aside", "nav"]):
        tag.decompose()

    # -------------------- TEXT COMPLET --------------------
    paragraphs = content.find_all(["p", "span", "div"])
    blocks = []
    for p in paragraphs:
        txt = p.get_text(" ", strip=True)
        if txt and len(txt) > 3:
            blocks.append(txt)

    if blocks:
        output["intro"] = blocks[0]
        output["full_text"] = "\n".join(blocks)

    # -------------------- SCOOP EXTRA SECTIONS --------------------
    text_lower = output["full_text"].lower()

    # 1. Keywords / cuvinte-cheie
    kw_candidates = ["cuvinte-cheie", "cuvinte cheie", "keywords"]
    output["keywords"] = _extract_section(blocks, kw_candidates)

    # 2. Cerințe tehnice / creative
    req_candidates = ["ce trebuie să faci", "cerințe", "provocarea", "brief", "tema"]
    output["requirements"] = _extract_section(blocks, req_candidates)

    # 3. Criterii de jurizare
    jury_candidates = ["jurizare", "cum se jurizează", "criterii", "punctaj"]
    output["jury_criteria"] = _extract_section(blocks, jury_candidates)

    # 4. Bonusuri
    bonus_candidates = ["bonus", "puncte bonus", "premiu suplimentar"]
    output["bonuses"] = _extract_section(blocks, bonus_candidates)

    # 5. Deadline
    for line in blocks:
        if "deadline" in line.lower() or "termen" in line.lower():
            output["deadline"] = line.strip()
            break

    # 6. Tema rezumat (folosește primele 1-2 paragrafe)
    if len(blocks) > 1:
        output["theme_summary"] = (blocks[0] + " " + blocks[1])[:450]

    # -------------------- SPONSORS --------------------
    sponsors = []
    for a in content.find_all("a", href=True):
        href = a["href"].strip()
        text = a.get_text(strip=True)

        if any(x in href.lower() for x in ["facebook", "twitter", "instagram", "mailto", "linkedin"]):
            continue
        if "super-blog.eu" in href or "superblog.eu" in href:
            continue

        name = text if len(text) >= 3 else href.replace("https://", "").replace("http://", "").split("/")[0]
        sponsors.append({"name": name, "url": href})

    unique = []
    seen = set()
    for s in sponsors:
        key = (s["name"], s["url"])
        if key not in seen:
            seen.add(key)
            unique.append(s)
    output["sponsors"] = unique

    # -------------------- IMAGES --------------------
    imgs = []
    for img in content.find_all("img", src=True):
        src = img["src"]
        if any(x in src.lower() for x in ["emoji", "icon", "avatar", "logo-svg"]):
            continue
        imgs.append(urljoin(url, src))
    output["images"] = imgs[:20]

    return output


# -------------------------------------------------------
# Helper: extract text sections based on keyword triggers
# -------------------------------------------------------
def _extract_section(blocks, keywords):
    found = []
    capture = False

    for line in blocks:
        line_low = line.lower()

        # activează capturarea dacă găsim headingul
        if any(key in line_low for key in keywords):
            capture = True
            continue

        # dacă e un heading major → oprește secțiunea
        if capture and (
            line.startswith("Proba") or
            "sponsor" in line_low or
            "punctaj" in line_low or
            "premii" in line_low or
            len(line.split()) < 2
        ):
            break

        if capture:
            found.append(line)

    return found
