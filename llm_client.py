from openai import OpenAI
import os

# Creează clientul OpenAI folosind cheia din variabila de mediu
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_article(extracted, style: str = "balanced"):
    """
    Generează un articol SuperBlog sub formă de poveste cinematică.
    """

    # ------------------ DATE PROBĂ ------------------
    probe_title = extracted.get("probe_title", "Articol SuperBlog")
    intro = extracted.get("intro", "")
    full_text = extracted.get("full_text", "")

    sponsors = extracted.get("sponsors", [])
    images = extracted.get("images", [])

    # Extra: cerințe, keywords, criterii jurizare etc.
    sb_keywords = extracted.get("keywords", [])
    sb_requirements = extracted.get("requirements", [])
    sb_jury = extracted.get("jury_criteria", [])
    sb_bonuses = extracted.get("bonuses", [])
    sb_deadline = extracted.get("deadline", "")
    sb_theme_summary = extracted.get("theme_summary", "")

    # ------------------ SPONSORI ------------------
    sponsor_links_text = ""
    for s in sponsors:
        name = (s.get("name") or "").strip()
        url = (s.get("url") or "").strip()
        if url:
            sponsor_links_text += f"- {name}: {url}\n"

    if not sponsor_links_text:
        sponsor_links_text = "(nu au fost detectați sponsori externi)"

    # ------------------ IMAGINI ------------------
    main_image = images[0] if len(images) > 0 else ""
    second_image = images[1] if len(images) > 1 else ""
    third_image = images[2] if len(images) > 2 else ""

    # ------------------ STILURI ------------------
    style_map = {
        "balanced": "Ton narativ echilibrat, emoțional dar clar.",
        "story": "Poveste cinematică, scene vizuale, descrieri bogate, dialoguri.",
        "marketing": "Narativ orientat spre beneficii, inspirațional, fără reclamă agresivă.",
        "journalistic": "Ton de reportaj narativ, observații personale, cadre scene.",
        "playful": "Ton jucăuș, cald, cu umor fin și imagini vii.",
        "formal": "Ton literar, sobru, elegant, cu fraze ample.",
    }
    style_instruction = style_map.get(style, style_map["story"])

    # ------------------ EXEMPLU SHORT (few-shot) ------------------
    example_article = """
<exemplu_superblog>
<h1>Exemplu – Poveste scurtă</h1>
<p>Era târziu, iar luminile difuze ale orașului învăluiau camera într-un calm electric.
Andrei privea ecranul, încercând să depășească un blocaj de comunicare. Un mic balon de chat
l-a surprins: un asistent virtual. A urmat o clipă de ezitare, apoi claritate. Traducerea
instantanee i-a permis să ajungă la celălalt. Așa s-a născut o conversație adevărată.</p>
</exemplu_superblog>
"""

    # ------------------ PROMPT FINAL ------------------
    prompt = f"""
Ești un scriitor premiat SuperBlog, cu un stil cinematografic și capacitatea de a integra
perfect cerințele tehnice într-o poveste literară.

SCOP OBLIGATORIU:
- Scrie o poveste COMPLETĂ, bogată, cinematică.
- MINIM 1000 de cuvinte. Întotdeauna peste 1000, niciodată sub.
- TOT conținutul să fie livrat DOAR ca HTML valid (<meta>, <h1>, <h2>, <p>, <figure> etc.)
- Fără markdown, fără explicații, fără text în afara HTML.

======================
DATELE PROBEI SUPERBLOG
======================

TITLU PROBĂ:
{probe_title}

REZUMAT TEMĂ (extras automat):
{sb_theme_summary}

INTRO:
{intro}

TEXT COMPLET PROBĂ:
{full_text}

Cuvinte-cheie detectate în probă:
{sb_keywords}

Cerințe tehnice și narative extrase:
{sb_requirements}

Criterii de jurizare:
{sb_jury}

Bonusuri:
{sb_bonuses}

Deadline:
{sb_deadline}

Linkuri sponsori:
{sponsor_links_text}

Imagini extrase:
- {main_image}
- {second_image}
- {third_image}

======================
CUM TREBUIE SĂ SCRII:
======================

- Articolul trebuie să fie o POVESTE, nu un advertorial.
- Personaj(e) clar definite, cu emoții, intenții, conflicte, rezolvări.
- Atmosferă cinematografică: culori, lumini, sunete, emoții.
- Dialoguri reale, naturale (măcar 3 dialoguri semnificative).
- Integrezi TOATE cerințele din probă în mod organic, natural.
- Integrezi cuvintele-cheie cerute în probă EXACT, natural, nu ca listă.
- Folosești imagini extrase, integrate ca scene în poveste cu <figure>.

STRUCTURĂ:
1) <meta name="description" content="...">
2) <h1>titlu poetic și memorabil</h1>
3) Povestea completă (MINIM 1000 cuvinte)
   - împărțită în scene <h2>, <h3>
   - descrieri vizuale
   - introspecție
   - conflict → evoluție → rezoluție
4) Imaginile integrate contextual:
   - Dacă există {main_image}, include un <figure> în prima jumătate a poveștii.
   - Dacă există {second_image}, include un <figure> în scena mediană.
   - Dacă există {third_image}, include un <figure> în scena finală.

STIL:
{style_instruction}

EXEMPLU DE TON (nu copia conținutul):
{example_article}

======================
CERINȚE TEHNICE FINALE
======================
- Textul final trebuie să fie DOAR HTML.
- MINIM 1000 cuvinte GARANTAT.
- Fără bullet-uri explicite. Dacă trebuie integrate, transformă-le în fraze narative.
- Fără text sau note în afara HTML.
"""

    # ------------------ APEL LA MODEL ------------------
    response = client.chat.completions.create(
        model="gpt-4.1",  # model foarte bun și stabil
        messages=[
            {
                "role": "system",
                "content": (
                    "Ești un autor premiat SuperBlog, stil literar, "
                    "povestitor cinematic, expert SEO și HTML."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        max_completion_tokens=6000,   # compatibil cu GPT-4.1+
        temperature=0.9,
    )

    return response.choices[0].message.content
