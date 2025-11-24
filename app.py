from flask import Flask, render_template, request, redirect, url_for
from scraper import extract_probe_data
from llm_client import generate_article
from wordpress_client import publish_post, WordPressError

from concurrent.futures import ThreadPoolExecutor
import threading
import uuid

app = Flask(__name__)

executor = ThreadPoolExecutor(max_workers=2)
tasks = {}
tasks_lock = threading.Lock()


def background_generate(task_id: str, probe_url: str, style: str):
    """Rulează generarea articolului în fundal."""
    try:
        extracted = extract_probe_data(probe_url)

        if extracted.get("error"):
            with tasks_lock:
                tasks[task_id]["status"] = "error"
                tasks[task_id]["error"] = extracted["error"]
            return

        article = generate_article(extracted, style)
        images = extracted.get("images", [])[:12]

        result = {
            "title": extracted.get("probe_title", "Proba SuperBlog"),
            "article": article,
            "images": images,
            "probe_url": probe_url,
        }

        with tasks_lock:
            tasks[task_id]["status"] = "done"
            tasks[task_id]["result"] = result

    except Exception as e:
        with tasks_lock:
            tasks[task_id]["status"] = "error"
            tasks[task_id]["error"] = str(e)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")

    probe_url = request.form.get("probe_url", "").strip()
    style = request.form.get("style", "balanced")

    if not probe_url:
        return render_template("index.html", error="Te rog introdu linkul probei SuperBlog.")

    # Creare task ID unic
    task_id = str(uuid.uuid4())
    with tasks_lock:
        tasks[task_id] = {"status": "pending", "result": None, "error": None}

    executor.submit(background_generate, task_id, probe_url, style)

    return redirect(url_for("task_status", task_id=task_id))


@app.route("/task/<task_id>", methods=["GET"])
def task_status(task_id):
    with tasks_lock:
        task = tasks.get(task_id)

    if task is None:
        return render_template(
            "task_status.html",
            status="missing",
            message="Task-ul nu a fost găsit sau a expirat. Te rog să reîncerci.",
            task_id=task_id,
            result=None,
        )

    if task["status"] == "pending":
        return render_template(
            "task_status.html",
            status="pending",
            message="Articolul se generează... Mai așteaptă câteva secunde și reîncarcă.",
            task_id=task_id,
            result=None,
        )

    if task["status"] == "error":
        return render_template(
            "task_status.html",
            status="error",
            message=f"Eroare la generare: {task.get('error')}",
            task_id=task_id,
            result=None,
        )

    # Task OK – rezultatul este gata
    result = task["result"]

    return render_template(
        "result.html",
        title=result["title"],
        article=result["article"],
        images=result["images"],
        probe_url=result["probe_url"],
    )


@app.route("/publish", methods=["POST"])
def publish():
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()

    if not title or not content:
        return render_template(
            "publish_result.html",
            success=False,
            message="Titlul sau conținutul lipsesc. Te rog verifică.",
            post_url=None,
        )

    try:
        wp_post = publish_post(title=title, content=content)
        post_url = wp_post.get("link")
        return render_template(
            "publish_result.html",
            success=True,
            message="Articolul a fost publicat cu succes în WordPress.",
            post_url=post_url,
        )

    except WordPressError as we:
        return render_template(
            "publish_result.html",
            success=False,
            message=f"Eroare WordPress: {we}",
            post_url=None,
        )

    except Exception as e:
        return render_template(
            "publish_result.html",
            success=False,
            message=f"Eroare neașteptată: {e}",
            post_url=None,
        )


if __name__ == "__main__":
    app.run(debug=True)
