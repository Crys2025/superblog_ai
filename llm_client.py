from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
Ești un autor de nivel literar, comparabil cu un scriitor celebru, creativ,
emoțional, profund și coerent. Scrii articole SuperBlog la nivel câștigător,
combinând:

– storytelling memorabil
– structură SEO impecabilă
– integrare naturală a cerințelor
– ton empatic și profesionist
– HTML complet compatibil WordPress

Ești în același timp expert SEO senior:
– folosești corect meta-descrieri
– titluri H1/H2/H3
– cuvinte-cheie integrate natural
– densitate optimă pentru Google
– imagini HTML (<figure>)
– linkuri sponsori
– claritate și indexare superioară

Eviti orice limbaj robotic. Scrii 100% uman, cald și expresiv.
"""


def generate_article_from_url(url: str, style: str):
    """
    Analizează complet pagina probei (GPT-5.1 cu browsing),
    extrage cerințele + imagini + linkuri + structură,
    și generează un articol COMPLET în HTML.
    """

    style_presets = {
        "balanced": "echilibrat, narativ, profesional, cu voce caldă și structură impecabilă.",
        "story": "puternic narativ, cinematic, emoțional, cu atmosferă și detalii senzoriale.",
        "marketing": "persuasiv, orientat pe beneficii, energic, clar și ușor de citit.",
        "journalistic": "obiectiv, solid, documentat, cu logică editorială și citate.",
        "playful": "jucăuș, amuzant, creativ, cu un ton prietenos.",
        "formal": "academic, elevat, riguros, cu formulari elegante."
    }

    chosen_style = style_presets.get(style, style_presets["balanced"])

    user_prompt = f"""
Analizează complet pagina probei de la linkul următor folosind browsing:

{url}

Extrage automat:
– titlul oficial al probei
– textul complet
– cerințele obligatorii tehnice
– sponsorii + linkurile acestora
– imaginile relevante (minim 3 dacă există)
– cuvintele-cheie cerute
– tonul recomandat
– informațiile suplimentare utile

Apoi generează un ARTICOL SUPERBLOG PREMIUM gata de publicat în WordPress,
conform cerințelor oficiale.

STRUCTURA OBLIGATORIE A ARTICOLULUI:

1) META-DESCRIERE (max 155 caractere, SEO)
   <meta name="description" content="...">

2) TITLU FINAL (stil {chosen_style})
   <h1>...</h1>

3) INTRODUCERE STORYTELLING (emoțională)
   – context
   – atmosferă
   – micro-poveste reală/ficțională

4) CORPUL ARTICOLULUI (H2 / H3)
   – integrare naturală a cuvintelor-cheie:
        * asistent virtual
        * translator vocal
        * traducere instantanee
   – integrare de linkuri către sponsori:
        * RoboChat → https://robochat.ro
        * Mobility → https://mobility.robochat.pro
   – exemple
   – povestiri
   – comparații „înainte/după”

5) IMAGINI ÎN HTML (minim 2–3)
   Folosește formatul:
   <figure>
       <img src="LINK" alt="descriere">
       <figcaption>descriere scurtă</figcaption>
   </figure>

6) SECTIUNE REFLECTIVĂ (creștere, viitor, umanitate)

7) CONCLUZIE EMOȚIONALĂ (memorabilă)

TONUL ARTICOLULUI PENTRU ACEST REQUEST:
– stil {chosen_style}
– 0% robotic
– 100% uman, cursiv, cald

GENEREAZĂ DOAR HTML, FĂRĂ EXPLICAȚII."""
    

    response = client.chat.completions.create(
        model="gpt-5.1",  # cea mai bună calitate
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        tools=[{"type": "web_browser"}],
        max_tokens=8000,
        temperature=0.85
    )

    return response.choices[0].message["content"]

