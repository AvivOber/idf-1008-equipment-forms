"""
Small self-service web page: a soldier types their name, the app looks them
up in the roster (name -> personal number + rank) and immediately returns
their filled-in, signed Form 1008 as a PDF download.
"""
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import io

import generator
import roster

app = Flask(__name__)
app.secret_key = "dev-only-not-for-production-secrets"


@app.route("/")
def index():
    return render_template("index.html", names=roster.all_names())


@app.route("/generate", methods=["POST"])
def generate():
    full_name = request.form.get("full_name", "").strip()
    if not full_name:
        flash("נא להזין שם מלא")
        return redirect(url_for("index"))

    soldier = roster.find_soldier(full_name)
    if not soldier:
        flash(f'לא נמצא חייל בשם "{full_name}" ברשימת החטיבה. פנה/י לאריק בורד.')
        return redirect(url_for("index"))

    try:
        pdf_bytes = generator.generate_form(
            soldier["full_name"], soldier["personal_number"], soldier["rank"]
        )
    except ValueError as e:
        flash(f"שגיאה ביצירת הטופס: {e}")
        return redirect(url_for("index"))

    filename = generator.safe_filename(soldier["full_name"], soldier["personal_number"])
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
