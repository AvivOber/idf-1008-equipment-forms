"""
Small self-service web page: a soldier types their name, the app looks them
up in the roster (name -> personal number + rank) and immediately returns
their filled-in, signed Form 1008 as a PDF download.

Also serves /admin: a password-protected page to upload/replace the roster
file from a browser (no terminal/Python needed) - the roster is gitignored
(it holds personal numbers), so a hosted deploy starts without one.
"""
import io
import os

from flask import Flask, render_template, request, send_file, flash, redirect, url_for, session

import config
import generator
import roster

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-not-for-production-secrets")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "changeme")


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
        flash(f'לא נמצא חייל בשם "{full_name}" ברשימת החטיבה. פנה/י ל{config.ISSUER["first_name"]} {config.ISSUER["last_name"]}.')
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


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST" and "password" in request.form:
        if request.form["password"] == ADMIN_PASSWORD:
            session["is_admin"] = True
        else:
            flash("סיסמה שגויה")
        return redirect(url_for("admin"))

    if not session.get("is_admin"):
        return render_template("admin_login.html")

    if request.method == "POST" and "roster_file" in request.files:
        f = request.files["roster_file"]
        if not f or not f.filename:
            flash("לא נבחר קובץ")
            return redirect(url_for("admin"))
        ext = f.filename.rsplit(".", 1)[-1].lower()
        if ext not in ("xlsx", "csv"):
            flash("יש להעלות קובץ xlsx או csv בלבד")
            return redirect(url_for("admin"))
        os.makedirs(os.path.dirname(config.ROSTER_XLSX), exist_ok=True)
        # A new file replaces whichever roster format was active before.
        for path in (config.ROSTER_XLSX, config.ROSTER_CSV):
            if os.path.exists(path):
                os.remove(path)
        target = config.ROSTER_XLSX if ext == "xlsx" else config.ROSTER_CSV
        f.save(target)
        try:
            count = len(roster.load_roster())
        except ValueError as e:
            flash(f"הקובץ הועלה אך יש בו בעיה: {e}")
            return redirect(url_for("admin"))
        flash(f"הרשימה עודכנה בהצלחה - {count} חיילים")
        return redirect(url_for("admin"))

    try:
        names = roster.all_names()
        error = None
    except ValueError as e:
        names = []
        error = str(e)
    return render_template("admin.html", names=names, error=error)


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
