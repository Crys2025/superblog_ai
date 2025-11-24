from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_article(extracted, style: str = "balanced"):
    probe_title = extracted.get("probe_title", "Articol SuperBlog")
    probe_intro = extracted.get("intro", "")
    full_text = extracted.get("full_text", "")
    sponsors = extracted.get("sponsors", [])
    images = extracted.get("images", [])

    sponsor_links_text = ""
    if sponsors:
        for s in sponsors:
            name = s.get("name", "").strip()
            url = s.get("url", "").strip()
            if name and url:
                sponsor_links_text += f"- <a href='{url}' target='_blank'>{name}</a>\n"
    else:
        sponsor_links_text = "- (Niciun sponsor detectat în această probă)"

    main_image = images[0] if images else ""

    style_map = {
        "story": "Ton narativ, cald, emoțional, cu exemple personale sau imaginare.",
        "marketing": "Ton orientat pe beneficii, clar, persuasiv, dar natural și etic.",
        "balanced": "Ton echilibrat între poveste și explicație, foarte potrivit pentru SuperBlog.",
        "journalistic": "Ton jurnalistic, informat, cu structură clară și argumente logice.",
        "playful": "Ton jucăuș, prietenos, cu umor fin și metafore.",
        "formal": "Ton mai serios, bine structurat, cu atenție la formulare și claritate.",
    }
    style_instruction = style_map.get(style, style_map["balanced"])

    example_article = """
<exemplu_superblog>
<h1>Exemplu SuperBlog – Cum tehnologia poate repara o conversație</h1>
<p>Uneori, cea mai dificilă parte într-o discuție nu este ceea ce spui, ci ceea ce celălalt înțelege. Ne pierdem în cuvinte, ton, emoții – iar o conversație care putea fi frumoasă se transformă într-o neînțelegere.</p>
<h2>Când cuvintele se lovesc de pereți</h2>
<p>Am trăit asta cu un coleg din altă țară. Eu încercam să explic o idee simplă, el încerca să mă înțeleagă. Nu ne certa nimeni, dar simțeam cum răbdarea ne scade cu fiecare propoziție.</p>
<h2>O tehnologie care nu îți răpește vocea, ci ți-o clarifică</h2>
<h3>Ce poate face un asistent modern?</h3>
<ul>
<li>ascultă fără să întrerupă și nu obosește</li>
<li>traduce intenții, nu doar cuvinte</li>
<li>lasă omul să fie om, fără presiune</li>
</ul>
<h3>De ce pare mai uman decât un om?</h3>
<p>Nu pentru că e mai bun, ci pentru că e mereu calm, rabdător și egal. Uneori, asta e tot ce avem nevoie pentru a continua discuția.</p>
<h2>O poveste scurtă</h2>
<p>Cu ajutorul unui translator vocal, am reușit să am în sfârșit o conversație firească cu acel coleg. Nu perfectă – dar clară. Și asta a schimbat totul.</p>
<h2>Concluzie</h2>
<p>Tehnologia potrivită nu înlocuiește oamenii, dar poate salva conversații, relații și timp. Într-o lume grăbită, poate fi sprijinul discret de care avem nevoie.</p>
</exemplu_superblog>
"""

    prompt = f"""
Ești un autor premiat SuperBlog, cu stil de scriitor celebru: expresiv, coerent, emoțional.
Ești și expert SEO: folosești H1-H3 corect, scrii meta descriere, integrezi natural cuvinte-cheie.

Scrii un articol COMPLET, în HTML, pentru o probă SuperBlog.

========================
EXEMPLU DE STIL SUPERBLOG:
{example_article}
========================

TITLUL PROBEI:
{probe_title}

INTRO DIN PROBĂ:
{probe_intro}

TEXT COMPLET AL PROBEI (DOAR CA SURSA DE INSPIRAȚIE, NU DE COPIAT):
{full_text}
========================

SPONSORII PROBEI (folosește-i în articol, cu linkuri HTML):
{sponsor_links_text}

========================
STRUCTURA OBLIGATORIE A ARTICOLULUI (HTML):

1) Meta descriere SEO sub formă de comentariu HTML:
<!-- meta-description: (max 155 de caractere, foarte atractivă și clară) -->

2) <h1>Titlu final atractiv, diferit de titlul oficial al probei, dar relevant</h1>

3) Introducere (1-3 paragrafe) – poveste scurtă, emoție, context.

4) <h2>Provocarea: când comunicarea se complică</h2>
   - descrie o situație dificilă de comunicare (om-om sau om-tehnologie).

5) <h2>Asistentul virtual care schimbă experiența</h2>
   <h3>Ce face diferit?</h3>
   - listă cu 3-5 beneficii clare (ul/li).
   <h3>De ce pare mai uman?</h3>
   - explică empatia digitală, claritatea, timpul câștigat.

6) <h2>Translatorul vocal cu traducere instantanee</h2>
   <h3>Exemplu narativ</h3>
   - poveste scurtă (reală sau imaginară) în care un translator vocal salvează situația.

7) <h2>Imagine reprezentativă</h2>
   - inserează un element <figure> cu o imagine relevantă, de forma:
     <figure>
         <img src="{main_image}" alt="Imagine din sursa probei" />
         <figcaption>Legendă scurtă.</figcaption>
     </figure>

8) <h2>Înainte și după: cum se transformă experiența</h2>
   - compară experiența fără tehnologie vs. cu tehnologie.

9) <h2>Concluzie</h2>
   - închide articolul cu un mesaj inspirațional.

========================
CUVINTE-CHEIE OBLIGATORII (INTEGREAZĂ-LE NATURAL):
- asistent virtual
- translator vocal
- traducere instantanee

========================
TON:
{style_instruction}

Nu copia fraze întregi din textul probei. Reformulează totul într-un stil original,
uman, fluent și plăcut de citit. Fără ton robotic, fără clișee de reclamă.

La final NU mai adăuga nimic în afara articolului HTML.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Ești un autor premiat SuperBlog, cu stil de scriitor celebru, și expert SEO."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2600,
        temperature=0.85,
    )

    return response.choices[0].message.content
