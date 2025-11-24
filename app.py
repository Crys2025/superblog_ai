from flask import Flask, render_template, request
from scraper import extract_data
from llm_client import generate_article

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        # --------------------
        # LINK PROBĂ — corectat
        # --------------------
        url = request.form.get("probe_url")
        if not url:
            return render_template("index.html", error="Te rog introdu un link valid.")

        # --------------------
        # STIL SCRIERE
        # --------------------
        style = request.form.get("style", "balanced")

        # --------------------
        # PARAMETRI PERSONALIZAȚI — corectați să coincidă cu index.html
        # --------------------
        min_words = int(request.form.get("min_words", 900))
        min_images = int(request.form.get("min_images", 2))
        max_images = int(request.form.get("max_images", 3))
        min_links = int(request.form.get("min_links", 2))

        # --------------------
        # CUVINTE-CHEIE PERSONALIZATE — corectate
        # --------------------
        raw_keywords = request.form.get("custom_keywords", "").strip()
        if raw_keywords:
            keywords = [k.strip() for k in raw_keywords.split(",") if k.strip()]
        else:
            keywords = None

        # --------------------
        # EXTRAGEREA DATELOR
        # --------------------
        extracted = extract_data(url)

        # --------------------
        # GENERARE ARTICOL
        # --------------------
        article = generate_article(
            extracted,
            style=style,
            target_words=min_words,
            min_images=min_images,
            max_images=max_images,
            min_links=min_links,
            required_keywords=keywords,
        )

        return render_template("result.html", article=article)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)


