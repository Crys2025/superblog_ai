from flask import Flask, render_template, request, jsonify
from concurrent.futures import ThreadPoolExecutor
import uuid

from scraper import extract_probe_data
from llm_client import generate_article

app = Flask(__name__)

# Executor pentru procesare în background (evită timeouts)
executor = ThreadPoolExecutor(max_workers=3)

# Task storage (simplu, doar în memorie)
TASKS = {}


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/", methods=["POST"])
def start_generation():
    # Preluăm linkul
    probe_url = request.form.get("probe_url")

    if not probe_url:
        return render_template("index.html", error="Te rog introdu un link valid.")

    # Stil de scriere
    style = request.form.get("style", "balanced")

    # Opțiuni avansate
    min_words = int(request.form.get("min_words", 900))
    min_images = int(request.form.get("min_images", 2))
    max_images = int(request.form.get("max_images", 3))
    min_links = int(request.form.get("min_links", 2))

    raw_keywords = request.form.get("custom_keywords", "").strip()
    if raw_keywords:
        custom_keywords = [k.strip() for k in raw_keywords.split(",") if k.strip()]
    else:
        custom_keywords = None

    # ID unic task
    task_id = str(uuid.uuid4())
    TASKS[task_id] = {"status": "running", "result": None}

    # Rulează în background
    executor.submit(
        run_generation_task,
        task_id,
        probe_url,
        style,
        min_words,
        min_images,
        max_images,
        min_links,
        custom_keywords,
    )

    return jsonify({"task_id": task_id, "redirect": f"/task/{task_id}"})


def run_generation_task(task_id, probe_url, style, min_words, min_images, max_images, min_links, custom_keywords):
    try:
        TASKS[task_id]["status"] = "extracting"

        extracted = extract_probe_data(probe_url)

        TASKS[task_id]["status"] = "generating"

        article = generate_article(
            extracted,
            style=style,
            target_words=min_words,
            min_images=min_images,
            max_images=max_images,
            min_links=min_links,
            required_keywords=custom_keywords,
        )

        TASKS[task_id]["status"] = "done"
        TASKS[task_id]["result"] = {
            "article": article,
            "probe_url": probe_url,
            "title": extracted.get("probe_title", "Articol generat"),
            "images": extracted.get("images", []),
        }
    except Exception as e:
        TASKS[task_id]["status"] = "error"
        TASKS[task_id]["result"] = str(e)


@app.route("/task/<task_id>")
def task_status(task_id):
    task = TASKS.get(task_id)
    if not task:
        return f"Task invalid: {task_id}", 404

    if task["status"] == "running" or task["status"] == "extracting" or task["status"] == "generating":
        return render_template("task_wait.html", task_id=task_id, status=task["status"])

    if task["status"] == "done":
        return render_template(
            "result.html",
            article=task["result"]["article"],
            probe_url=task["result"]["probe_url"],
            title=task["result"]["title"],
            images=task["result"]["images"],
        )

    return f"Eroare la generare: {task['result']}", 500


if __name__ == "__main__":
    app.run(debug=True)
