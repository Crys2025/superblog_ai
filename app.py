from flask import Flask, render_template, request
from scraper import extract_data
from llm_client import generate_article

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        # LINK PROBĂ – numele corect este "probe_url"
        url = request.form.get("probe_url")
        if not url:
            return render_template("index.html", error="Te rog introdu un link valid.")

        # STIL SCRIERE
        style = request.form.get("style", "balanced")

        # ======================
        #   OPȚIUNI AVANSATE
        # ======================

        # MIN WORDS – numele din form = min_words
        try:
            target_words = int(request.form.get("min_words", 900))
        except:
            target_words = 900

        # IMAGINI
        min_images = int(request.form.get("min_images", 2))
        max_images = int(request.form.get("max_images", 3))

        # LINKURI
        min_links = int(request.form.get("min_links", 2))

        # KEYWORDS – numele corect = custom_keywords
        raw_keywords = request.form.get("custom_keywords", "").strip()
        if raw_keywords:
            keywords = [k.strip() for k in raw_keywords.split(",") if k.strip()]
        else:
            keywords = None

        # ======================
        # SCRAPER
        # ======================
        extracted = extract_data(url)

        if "error" in extracted:
            return render_template("index.html", error=extracted["error"])

        # ======================
        # ARTICLE
        # ======================
        article = generate_article(
            extracted,
            style=style,
            target_words=target_words,
            min_images=min_images,
            max_images=max_images,
            min_links=min_links,
            required_keywords=keywords,
        )

        return render_template(
            "result.html",
            article=article,
            title=extracted.get("probe_title", "Articol generat"),
            probe_url=url,
            images=extracted.get("images", [])
        )

    return render_template("index.html")


# ======================
#   PUBLISH (opțional)
# ======================
@app.route("/publish", methods=["POST"])
def publish():
    return "Funcția de publicare nu este încă activată."


if __name__ == "__main__":
    app.run(debug=True)



