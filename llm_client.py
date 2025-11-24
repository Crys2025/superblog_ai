from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_article(extracted, style: str = "balanced"):
    """
    Generator de articole SuperBlog, stil scriitor celebru + SEO,
    cu structură HTML completă, linkuri și imagini integrate.

    Folosește:
    - textul probei (full_text, intro)
    - sponsorii extrași (nume + link)
    - imaginile extrase (lista images)
    """

    probe_title = extracted.get("probe_title", "Articol SuperBlog")
    probe_intro = extracted.get("intro", "")
    full_text = extracted.get("full_text", "")
    sponsors = extracted.get("sponsors", [])
    images = extracted.get("images", [])

    # ---------------------------------------------------------
    # Construim blocul textual cu sponsorii (pentru prompt)
    # ---------------------------------------------------------
    sponsor_links_text = ""
    if sponsors:
        for s in sponsors:
            name = s.get("name", "").strip()
            url = s.get("url", "").strip()
            if name and url:
                sponsor_links_text += f"- {name}: {url}\n"
    else:
        sponsor_links_text = "- (Niciun sponsor clar detectat în probă)"

    # ---------------------------------------------------------
    # Imagini – folosim până la 3 pentru articol
    # ---------------------------------------------------------
    main_image = images[0] if len(images) > 0 else ""
    second_image = images[1] if len(images) > 1 else ""
    third_image = images[2] if len(images) > 2 else ""

    # ---------------------------------------------------------
    # Stiluri posibile
    # ---------------------------------------------------------
    style_map = {
        "balanced": "Ton echilibrat, cald, narativ + explicativ, ideal pentru SuperBlog.",
        "story": "Ton puternic narativ, emoțional, cu detalii și atmosferă.",
        "marketing": "Ton persuasiv, orientat pe beneficii, dar prietenos și etic.",
        "journalistic": "Ton jurnalistic, bine structurat, cu logică și explicații clare.",
        "playful": "Ton jucăuș, cu umor fin, metafore și energie pozitivă.",
        "formal": "Ton mai serios, elevat, bine structurat, cu fraze curate.",
    }
    style_instruction = style_map.get(style, style_map["balanced"])

    # ---------------------------------------------------------
    # Exemplu de structură (few-shot foarte scurt, DOAR ca stil)
    # ---------------------------------------------------------
    example_article = """
<exemplu_superblog>
<h1>Exemplu – Când tehnologia repară o conversație</h1>
<p>Uneori, cea mai dificilă parte a unei discuții nu este ceea ce spui, ci ceea ce celălalt înțelege. O propoziție mică poate aprinde o furtună de interpretări, iar totul pornește de la o nuanță de ton sau un cuvânt ales neinspirat.</p>
<h2>Când cuvintele nu ajung unde trebuie</h2>
<p>Mi s-a întâmplat să vorbesc cu un coleg din altă țară și să simt că, deși folosim aceeași limbă, trăim în conversații paralele. Eu explicam, el înțelegea altceva. Nu din răutate, ci din lipsă de claritate.</p>
<h2>Un asistent virtual care aduce liniște în dialog</h2>
<p>Un asistent virtual nu obosește, nu ridică tonul, nu se enervează. El traduce întrebările și răspunsurile în mesaje clare, pas cu pas. Iar când la mijloc apare și un translator vocal, barierele de limbă dispar și rămâne doar ideea.</p>
<h2>Concluzie</h2>
<p>Tehnologia nu ține loc de inimă sau empatie, dar poate fi puntea care ne lasă să ne vedem unii pe alții mai limpede. Iar uneori, asta este tot ce avem nevoie.</p>
</exemplu_superblog>
"""

    # ---------------------------------------------------------
    # PROMPT – extrem de clar: DOAR HTML, FĂRĂ ``` !!!
    # ---------------------------------------------------------
    prompt = f"""
Ești un autor premiat SuperBlog, cu stil de scriitor celebru (expresiv, emoțional, coerent)
și expert SEO (structură, meta, H1–H3, cuvinte-cheie, lizibilitate).

Scopul: generezi un ARTICOL COMPLET, GATA DE PUBLICAT, pentru proba:

TITLUL OFICIAL AL PROBEI:
{probe_title}

INTRO DIN PROBĂ:
{probe_intro}

TEXT COMPLET AL PROBEI (doar ca material de lucru, nu de copiat mot-a-mot):
{full_text}

SPONSORII DETECTAȚI ÎN PROBĂ:
{sponsor_links_text}

IMAGINI DISPONIBILE (de folosit în <figure>):
- main_image: {main_image}
- second_image: {second_image}
- third_image: {third_image}

================================================================
EXEMPLU DE STIL (NU de copiat, doar ca referință de ton și structură):
{example_article}
================================================================

CERINȚE OBLIGATORII PENTRU ARTICOL:

1) RĂSPUNSUL TĂU TREBUIE SĂ FIE DOAR HTML VALID.
   - NU folosi ``` sau blocuri de cod.
   - NU adăuga explicații înainte sau după articol.
   - Începe direct cu tagul <meta> sau <h1>.

2) INCLUDE O META DESCRIERE SEO:
   <meta name="description" content="maxim 155 de caractere, clar, atractiv, cu idee centrală">

3) INCLUDE UN TITLU FERMECĂTOR:
   <h1>un titlu creativ, diferit de titlul oficial al probei, dar relevant</h1>

4) STRUCTURĂ CLARĂ, CU H2 / H3:
   - <h2>Provocarea: când comunicarea se complică</h2>
   - <h2>Asistentul virtual care schimbă experiența</h2>
       <h3>Ce face diferit?</h3>
       <ul>3–5 beneficii clare (disponibilitate, claritate, timp câștigat etc.)</ul>
       <h3>De ce pare mai uman?</h3>
       <p>explică empatia digitală, tonul calm, răbdarea, claritatea</p>

   - <h2>Translatorul vocal cu traducere instantanee</h2>
       <h3>Exemplu narativ</h3>
       <p>poveste scurtă, concretă (reală sau imaginară) în care un translator vocal salvează conversația</p>

   - <h2>Înainte și după: cum se transformă experiența</h2>
       <p>compară o situație fără tehnologie vs. una cu asistent virtual + translator vocal</p>

   - <h2>Concluzie</h2>
       <p>mesaj inspirațional, uman, care să lase cititorul cu o emoție și o idee clară</p>

5) IMAGINI ÎNTEGRATE ÎN ARTICOL (dacă există linkuri):
   – Dacă {main_image} nu este gol, inserează:
     <figure>
         <img src="{main_image}" alt="Imagine din sursa probei">
         <figcaption>O reprezentare vizuală a comunicării asistate de tehnologie.</figcaption>
     </figure>

   – Dacă {second_image} există, inserează într-o secțiune relevantă (de ex. la translator vocal):
     <figure>
         <img src="{second_image}" alt="Imagine asociată Mobility sau traducerii instantanee">
         <figcaption>Tehnologia care traduce vocea în timp real.</figcaption>
     </figure>

   – Dacă {third_image} există, inserează în apropierea concluziei sau a ideii de viitor.

6) LINKURI CĂTRE SPONSORI (DACĂ EXISTĂ ÎN SPONSORS):
   – Dacă printre sponsori se regăsește un link care conține "robochat":
       Folosește-l într-un paragraf de forma:
       <a href="LINK_ROBOCHAT" target="_blank">RoboChat</a>

   – Dacă există un link care conține "mobility.robochat.pro":
       Folosește-l într-un paragraf de forma:
       <a href="LINK_MOBILITY" target="_blank">Mobility</a>

   – Dacă nu e găsit nimic, poți folosi aceste linkuri implicite:
       <a href="https://robochat.ro" target="_blank">RoboChat</a>
       <a href="https://mobility.robochat.pro" target="_blank">Mobility</a>

7) CUVINTE-CHEIE OBLIGATORII:
   Integrează NATURAL (fără listă artificială) următoarele expresii:
   – asistent virtual
   – translator vocal
   – traducere instantanee

8) TONUL ARTICOLULUI:
   Stil: {style_instruction}
   – 0% ton robotic
   – 100% uman, fluid, coerent, cu fraze frumoase, dar clare
   – combinație de poveste + reflecție + beneficii practice
   – respectă cât mai fidel spiritul și tema reală a probei (nu inventa cerințe)

IMPORTANT:
– NU încadra răspunsul în ``` sau în alt tip de bloc de cod.
– Răspunsul tău trebuie să fie DOAR HTML, gata de copiat în WordPress.
"""

    response = client.chat.completions.create(
        model="gpt-4.1",  # model puternic, bun pentru astfel de task-uri
        messages=[
            {
                "role": "system",
                "content": (
                    "Ești un autor premiat SuperBlog, cu stil de scriitor celebru, "
                    "și expert SEO în structura articolelor pentru bloguri WordPress."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=3500,
        temperature=0.8,
    )

    # noul SDK folosește .message.content
    return response.choices[0].message.content


