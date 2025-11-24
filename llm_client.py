from openai import OpenAI
import os

# Creează clientul OpenAI folosind cheia din variabila de mediu
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_article(
    extracted,
    style: str = "balanced",
    target_words: int = 900,
    min_images: int = 2,
    max_images: int = 4,
    min_links: int = 2,
    required_keywords=None,
):
    """
    Generează un articol SuperBlog sub formă de POVESTE cinematică,
    integrând natural:
      - cerințele din enunțul probei (text, ton)
      - sponsorii și linkurile lor
      - imaginile disponibile
      - cuvintele-cheie obligatorii (implicit):
          * asistent virtual
          * translator vocal
          * traducere instantanee

    Parametri de control (pentru dropdown-uri în UI):
      - style: tipul de stil (balanced, story, marketing, journalistic, playful, formal)
      - target_words: număr minim de cuvinte (ex: 800, 900, 1200)
      - min_images: număr minim de imagini <figure> de integrat
      - max_images: număr maxim de imagini (dacă există suficiente)
      - min_links: număr minim de linkuri <a href="...">
      - required_keywords: listă de cuvinte-cheie de integrat în text;
        dacă este None, se folosește setul standard pentru proba RoboChat/Mobility.

    `extracted` este dict-ul de la scraper.py și conține:
      - probe_title
      - intro
      - full_text
      - sponsors: list[{"name", "url"}]
      - images: list[str]
    """

    # ------------------ DATE PROBĂ ------------------
    probe_title = extracted.get("probe_title", "Articol SuperBlog")
    probe_intro = extracted.get("intro", "")
    full_text = extracted.get("full_text", "")
    sponsors = extracted.get("sponsors", [])
    images = extracted.get("images", [])

    # ------------------ SPONSORI ------------------
    sponsor_links_text = ""
    robochat_url = None
    mobility_url = None

    if sponsors:
        for s in sponsors:
            name = (s.get("name") or "").strip()
            url = (s.get("url") or "").strip()
            if not url:
                continue

            # păstrăm listă textuală pentru prompt
            sponsor_links_text += f"- {name or url}: {url}\n"

            low_url = url.lower()
            if "robochat.ro" in low_url and robochat_url is None:
                robochat_url = url
            if "mobility.robochat.pro" in low_url and mobility_url is None:
                mobility_url = url
    else:
        sponsor_links_text = "- (Nu s-au detectat sponsori din probă – se vor folosi linkurile implicite.)"

    # fallback-uri dacă nu s-au detectat din probă
    if robochat_url is None:
        robochat_url = "https://robochat.ro"
    if mobility_url is None:
        mobility_url = "https://mobility.robochat.pro"

    # ------------------ IMAGINI ------------------
    # Folosim câte imagini avem, dar nu mai multe decât max_images
    limited_images = images[: max_images] if images else []
    # Vom explica în prompt cum să folosească între min_images și max_images din aceste linkuri

    # ------------------ CUVINTE-CHEIE ------------------
    if required_keywords is None or not isinstance(required_keywords, (list, tuple)) or len(required_keywords) == 0:
        required_keywords = [
            "asistent virtual",
            "translator vocal",
            "traducere instantanee",
        ]

    # ------------------ STILURI ------------------
    style_map = {
        "balanced": "Ton narativ + explicativ, echilibrat, potrivit pentru un articol de blog literar, dar clar.",
        "story": "Ton puternic narativ, cinematic, emoțional, cu dialoguri și scene vizuale.",
        "marketing": "Ton narativ cu accent pe beneficii și transformare, dar nu agresiv, ci cald.",
        "journalistic": "Ton narativ-jurnalistic, ca un reportaj cu personaje și trăiri.",
        "playful": "Ton narativ jucăuș, cu umor fin și imagini vii.",
        "formal": "Ton narativ mai sobru, elegant, cu fraze lungi și bine așezate.",
    }
    style_instruction = style_map.get(style, style_map["story"])

    # ------------------ EXEMPLU DE STIL (few-shot scurt) ------------------
    example_article = """
<exemplu_superblog>
<h1>Exemplu – O conversație salvată de tehnologie</h1>
<p>Era târziu, iar luminile orașului se vedeau în reflexia ecranului de laptop. Andrei își trecu mâna prin păr, pentru a nu știu câta oară, încercând să explice aceeași idee unui colaborator din altă țară. Cuvintele se loveau de un zid invizibil, iar tăcerile deveneau tot mai grele.</p>
<p>Într-un moment de frustrare, privirea i-a căzut pe un mic balon de chat din colțul site-ului. „Pot să te ajut?”, scria acolo. Era un asistent virtual. Fără să mai gândească prea mult, a dat click. Întrebările clare și răspunsurile concise l-au ajutat să-și structureze mesajul. Apoi, un translator vocal cu traducere instantanee a făcut restul: vocea lui era auzită limpede, în limba partenerului.</p>
<p>Deodată, expresia de pe chipul interlocutorului s-a schimbat. Din confuzie în înțelegere. Din tensiune în colaborare. Nu tehnologia ținuse loc de empatie, dar o făcuse posibilă.</p>
</exemplu_superblog>
"""

    # ------------------ PREGĂTIM LISTA DE IMAGINI PENTRU PROMPT ------------------
    if limited_images:
        images_for_prompt = "\n".join(
            f"{idx + 1}) {url}" for idx, url in enumerate(limited_images)
        )
    else:
        images_for_prompt = "(Nu există imagini detectate în probă.)"

    # ------------------ PREGĂTIM LISTA DE CUVINTE-CHEIE ------------------
    keywords_for_prompt = "\n".join(f"- {kw}" for kw in required_keywords)

    # ------------------ PROMPT – DOAR HTML, POVESTE COMPLETĂ ------------------
    prompt = f"""
Ești un scriitor premiat, cu nivel literar (nu doar blogger), obișnuit să creeze
povești cinematice și emoționale. În același timp, știi să respecți cerințe
tehnice SuperBlog (cuvinte-cheie, linkuri, imagini, lungime minimă) fără ca
textul să pară publicitar sau artificial.

Scrie un ARTICOL SUPERBLOG SUB FORMĂ DE POVESTE COMPLETĂ, în care:

- TOTUL este o poveste cu personaje, scene, atmosferă și emoții.
- Nu scrii bullet-uri seci, ci le integrezi în descriere, dialog, gânduri.
- Cuvintele-cheie, linkurile și imaginile sunt topite în narațiune, nu puse ca listă.

==============================
INFORMAȚII DIN PROBĂ:
==============================

TITLU OFICIAL PROBĂ:
{probe_title}

INTRO PROBĂ:
{probe_intro}

TEXT COMPLET PROBĂ (NU îl copia întocmai, doar înțelege tema și cerințele):
{full_text}

SPONSORI DETECTAȚI:
{sponsor_links_text}

LINKURI PRINCIPALE PENTRU POVESTE:
- RoboChat: {robochat_url}
- Mobility: {mobility_url}

IMAGINI DISPONIBILE (de folosit în articol):
{images_for_prompt}

==============================
CERINȚE CONFIGURABILE (DIN UI):
==============================

1) LUNGIME TEXT:
   - Articolul trebuie să aibă CEL PUȚIN {target_words} cuvinte.
   - Dacă inițial povestea e mai scurtă, continuă cu:
       * descriere de atmosferă
       * detalii emoționale
       * dialoguri suplimentare
       * reflecții ale personajului
   până când ajungi la cel puțin {target_words} cuvinte.

2) IMAGINI:
   - Integrează între {min_images} și {max_images} imagini <figure>, dacă există suficiente linkuri.
   - Folosește linkurile de mai sus în momente-cheie ale poveștii
     (când personajul descoperă site-ul, când folosește tehnologia, când trage concluzia).
   - Fiecare imagine trebuie să fie însoțită de:
       <figure>
           <img src="LINK" alt="descriere scurtă, clară">
           <figcaption>legendă scurtă, poetică, dar clară.</figcaption>
       </figure>

3) LINKURI:
   - Folosește CEL PUȚIN {min_links} linkuri <a href="..."> în text.
   - Minim:
       * un link către RoboChat: <a href="{robochat_url}" target="_blank">RoboChat</a>
       * un link către Mobility: <a href="{mobility_url}" target="_blank">Mobility</a>
   - Poți integra și alte linkuri din lista sponsorilor, dacă sunt relevante, dar fără reclamă agresivă.

4) CUVINTE-CHEIE (OBLIGATORIU DE INCLUS NATURAL ÎN POVESTE):
{keywords_for_prompt}

   - Folosește fiecare cuvânt-cheie cel puțin o dată.
   - Integrează-le în propoziții firești, de exemplu:
       „a descoperit un asistent virtual pe site…”
       „a pornit un translator vocal cu traducere instantanee…”
   - Nu face listă de cuvinte-cheie; trebuie să fie organic în text.

5) STIL DE SCRIERE:
   Stil selectat: {style} → {style_instruction}
   - păstrează tonul narativ cinematic
   - descrieri vizuale
   - dialoguri (1–3 dialoguri scurte)
   - introspecție (personajul își pune întrebări, simte, reacționează)
   - fără ton de reclamă, fără superlative goale.

==============================
STRUCTURĂ CERUTĂ (DAR TOTUL CA POVESTE):
==============================

Răspunsul tău trebuie să fie DOAR HTML, astfel:

1) META-DESCRIERE SEO (max 155 caractere, rezumă emoția poveștii):
   <meta name="description" content="...">

2) TITLU (poetic, atractiv, de tip literar, dar clar):
   <h1>...</h1>

3) TEXT NARATIV (povestea completă, {target_words}+ cuvinte):
   - Poți folosi <h2> sau <h3> ca „capitole” ale poveștii (ex: <h2>Dimineața în care totul a sunat greșit</h2>),
     dar nu scrie ca într-un manual, ci ca într-o nuvelă.

4) INTEGRAREA IMAGINILOR:
   - Folosește între {min_images} și {max_images} <figure> cu imaginile din lista de mai sus, dacă există suficiente.

5) CUVINTE-CHEIE:
   - Include toate cuvintele-cheie specificate, natural, în fraze.

==============================
EXEMPLU DE STIL (DOAR CA REFERINȚĂ, NU DE COPIAT):
==============================
{example_article}

==============================
CERINȚE TEHNICE FINALE:
==============================

- Răspunsul tău trebuie să fie DOAR HTML.
- Nu folosi ``` sau blocuri de cod.
- Nu adăuga explicații în afara articolului.
- Nu scrie text în afara tagurilor HTML.
"""

    # ------------------ APEL LA MODEL ------------------
    response = client.chat.completions.create(
        model="gpt-5.1",  # model mai puternic (ChatGPT 5.1)
        messages=[
            {
                "role": "system",
                "content": (
                    "Ești un autor premiat SuperBlog, cu stil de scriitor celebru, "
                    "și expert SEO în structurarea articolelor HTML pentru bloguri WordPress. "
                    "Scrii povești care par 100% umane, nu generate de AI. "
                    "Respecți strict cerințele de lungime minimă, imagini, linkuri și cuvinte-cheie."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=4500,
        temperature=0.9,
    )

    # în noul SDK, conținutul este în .message.content
    return response.choices[0].message.content




