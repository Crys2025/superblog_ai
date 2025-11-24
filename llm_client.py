from openai import OpenAI
import os

# Creează clientul OpenAI folosind cheia din variabila de mediu
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_article(extracted, style: str = "balanced"):
    """
    Generează un articol SuperBlog sub formă de POVESTE cinematică,
    integrând natural:
      - cerințele din enunțul probei (text, ton)
      - sponsorii și linkurile lor
      - imaginile disponibile
      - cuvintele-cheie obligatorii:
          * asistent virtual
          * translator vocal
          * traducere instantanee

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
    main_image = images[0] if len(images) > 0 else ""
    second_image = images[1] if len(images) > 1 else ""
    third_image = images[2] if len(images) > 2 else ""

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

    # ------------------ PROMPT – DOAR HTML, POVESTE COMPLETĂ ------------------
    prompt = f"""
Ești un scriitor premiat, cu nivel literar (nu doar blogger), obișnuit să creeze
povești cinematice și emoționale. În același timp, știi să respecți cerințe
tehnice SuperBlog (cuvinte-cheie, linkuri, imagini) fără ca textul să pară
publicitar sau artificial.

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

IMAGINI DISPONIBILE:
1) {main_image}
2) {second_image}
3) {third_image}

==============================
OBIECTIV:
==============================

Creează o poveste în care personajul principal trece printr-o situație în care
comunicarea eșuează (la muncă, într-o călătorie, într-o conversație importantă).
Te rog:

- să arăți frustrarea, emoțiile, zidurile invizibile între oameni;
- apoi să lași tehnologia să apară ca sprijin (nu erou salvator),
  sub forma:
    * unui asistent virtual (RoboChat)
    * unui translator vocal cu traducere instantanee (Mobility);

- să integrezi tehnologia astfel:
    * Personajul descoperă un asistent virtual pe un site și vede că îl ajută
      să formuleze, să clarifice, să răspundă (asistent virtual).
    * Personajul folosește un translator vocal cu traducere instantanee pentru
      a vorbi cu cineva din altă țară sau alt context (translator vocal, traducere instantanee).

- să introduci linkurile în mod NATURAL:
    * de exemplu: „a deschis site-ul <a href=\\"{robochat_url}\\" target=\\"_blank\\">RoboChat</a>”
    * și: „a activat <a href=\\"{mobility_url}\\" target=\\"_blank\\">Mobility</a>, un translator vocal cu traducere instantanee”

==============================
STRUCTURĂ CERUTĂ (DAR TOTUL CA POVESTE):
==============================

Răspunsul tău trebuie să fie DOAR HTML, astfel:

1) META-DESCRIERE SEO (max 155 caractere, rezumă emoția poveștii):
   <meta name="description" content="...">

2) TITLU (poetic, atractiv, de tip literar, dar clar):
   <h1>...</h1>

3) TEXT NARATIV (povestea completă, 800+ cuvinte):
   - nu pune subtitluri „tehnice” gen „Asistentul virtual care...” ca H2 separate,
     decât dacă le integrezi foarte natural în ton narativ;
   - poți folosi <h2> sau <h3> ca „capitole” ale poveștii (ex: <h2>Dimineața în care totul a sunat greșit</h2>),
     dar nu scrie ca într-un manual, ci ca într-o nuvelă.

4) INTEGRAREA IMAGINILOR:
   - Dacă {main_image} nu e gol, integrează-l într-un moment cheie al poveștii,
     de exemplu când personajul deschide site-ul / vede chatbotul:

     <figure>
         <img src="{main_image}" alt="Imagine asociată poveștii și tehnologiei">
         <figcaption>O fereastră mică de chat care schimbă o conversație mare.</figcaption>
     </figure>

   - Dacă {second_image} există, integreaz-o în scena în care apare translatorul vocal Mobility.
   - Dacă {third_image} există, integreaz-o spre final, ca simbol al unei lumi
     în care oamenii și tehnologia se ascultă.

5) CUVINTE-CHEIE OBLIGATORII (DE INTEGRAT NATURAL ÎN POVESTE):
   - asistent virtual
   - translator vocal
   - traducere instantanee

   NU le pune ca listă. Folosește-le în propoziții firești.

6) TON:
   Stil: {style_instruction}
   – cinematic
   – cu descrieri vizuale
   – cu dialoguri (măcar în 1-2 locuri)
   – cu introspecție (personajul își pune întrebări, are trăiri)
   – fără ton de reclamă, fără superlative goale.

7) EXEMPLU DE STIL (DOAR CA REFERINȚĂ, NU DE COPIAT):
{example_article}

==============================
CERINȚE TEHNICE FINALE:
==============================

- Răspunsul tău trebuie să fie DOAR HTML.
- Nu folosi ``` sau blocuri de cod.
- Nu adăuga explicații în afara articolului.
- Nu scrie metasau text în afara tagurilor HTML.
"""

    # ------------------ APEL LA MODEL ------------------
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # model compatibil și suficient de bun + ieftin
        messages=[
            {
                "role": "system",
                "content": (
                    "Ești un autor premiat SuperBlog, cu stil de scriitor celebru, "
                    "și expert SEO în structurarea articolelor HTML pentru bloguri WordPress. "
                    "Scrii povești care par 100% umane, nu generate de AI."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=5000,
        temperature=0.9,
    )

    # în noul SDK, conținutul este în .message.content
    return response.choices[0].message.content
