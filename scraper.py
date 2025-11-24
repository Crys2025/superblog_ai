import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_data(url: str) -> dict:
    output = {
        "probe_title": "",
        "intro": "",
        "full_text": "",
        "sponsors": [],
        "images": [],
    }

    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
    except Exception as e:
        return {"error": f"Eroare la accesarea linkului: {e}"}

    soup = BeautifulSoup(response.text, "html.parser")

    title_tag = soup.find("h1", class_="entry-title") or soup.find("h1")
    if title_tag:
        output["probe_title"] = title_tag.get_text(strip=True)

    content = soup.find("div", class_="entry-content")
    if not content:
        content = soup.find("article")
    if not content:
        return {"error": "Nu am putut localiza conținutul principal al probei."}

    for tag in content.find_all(["script", "style", "aside", "nav"]):
        tag.decompose()

    paragraphs = content.find_all(["p", "span", "div"])
    text_blocks = [p.get_text(" ", strip=True) for p in paragraphs if p.get_text(strip=True)]

    if text_blocks:
        output["intro"] = text_blocks[0]
        output["full_text"] = "\n".join(text_blocks)

    sponsors = []
    for a in content.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True)
        if ("super-blog.eu" in href) or ("superblog.eu" in href):
            continue
        if any(x in href.lower() for x in ["facebook", "twitter", "instagram", "mailto", "linkedin"]):
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

    images = []
    for img in content.find_all("img", src=True):
        src = img["src"]
        if any(x in src.lower() for x in ["emoji", "icon", "avatar", "logo-svg"]):
            continue
        img_url = urljoin(url, src)
        images.append(img_url)

    output["images"] = images[:15]

    return output
