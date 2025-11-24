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
    }

    # -------------------- FETCH PAGE --------------------
    try:
        response = requests.get(url, timeout=25)
        response.raise_for_status()
    except Exception as e:
        return {"error": f"Eroare la accesarea linkului: {e}"}

    soup = BeautifulSoup(response.text, "html.parser")

    # -------------------- TITLU --------------------
    title_tag = (
        soup.find("h1", class_="entry-title")
        or soup.find("h1", class_="tdb-title-text")
        or soup.find("h1")
    )

    if title_tag:
        output["probe_title"] = title_tag.get_text(strip=True)

    # -------------------- CONTENT CATCH-ALL --------------------
    POSSIBLE_CONTENT_SELECTORS = [
        "div.entry-content",
        "div.td-post-content",
        "div.tdb-block-inner",
        "article div.td-post-content",
        "article",
    ]

    content = None
    for selector in POSSIBLE_CONTENT_SELECTORS:
        content = soup.select_one(selector)
        if content:
            break

    if not content:
        return {"error": "Nu am putut găsi conținutul principal al probei."}

    # Curățare taguri inutile
    for tag in content.find_all(["script", "style", "aside", "nav", "header", "footer"]):
        tag.decompose()

    # -------------------- TEXT --------------------
    paragraphs = content.find_all(["p", "span", "div"])
    text_blocks = []

    for p in paragraphs:
        txt = p.get_text(" ", strip=True)
        if txt and len(txt) > 3:
            text_blocks.append(txt)

    if text_blocks:
        output["intro"] = text_blocks[0]
        output["full_text"] = "\n".join(text_blocks)

    # -------------------- SPONSORS (LINKS) --------------------
    sponsors = []
    for a in content.find_all("a", href=True):
        href = a["href"].strip()
        text = a.get_text(strip=True)

        if any(x in href.lower() for x in ["facebook", "twitter", "instagram", "mailto", "linkedin"]):
            continue

        # Nu vrem linkuri interne SB
        if "super-blog.eu" in href or "superblog.eu" in href:
            continue

        name = text if len(text) >= 3 else href.replace("https://", "").replace("http://", "").split("/")[0]
        sponsors.append({"name": name, "url": href})

    # unicizare
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
