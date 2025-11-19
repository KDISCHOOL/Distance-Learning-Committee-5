from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from config import Config
from models import db, Faculty, CourseModality
from utils import enrich_faculty_excel, normalize_name, fuzzy_search_name, format_modified_date, import_course_excel
from io import BytesIO
from datetime import datetime, timezone
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route("/")
    def index():
        return render_template("index.html")

    # ---------- Faculty: admin upload to enrich DB (admin-only) ----------
    @app.route("/admin/upload/faculty", methods=["GET", "POST"])
    def admin_upload_faculty():
        if request.method == "POST":
            pin = request.form.get("admin_pin", "")
            if pin != app.config["ADMIN_PIN"]:
                flash("Admin PIN incorrect", "danger")
                return redirect(url_for("admin_upload_faculty"))
            file = request.files.get("file")
            if not file:
                flash("No file uploaded", "warning")
                return redirect(url_for("admin_upload_faculty"))
            # Import and merge into Faculty table: for this app we assume upload contains full rows
            import_pandas_handle = request.files.get("file")
            # Basic import: if "Korean_name" present, use to upsert
            import pandas as pd
            df = pd.read_excel(import_pandas_handle, engine="openpyxl")
            # Expect columns: No, Korean_name, English_name, Category, Email
            for _, row in df.iterrows():
                kname = normalize_name(row.get("Korean_name", ""))
                if not kname:
                    continue
                existing = Faculty.query.filter_by(korean_name=kname).first()
                if existing:
                    existing.english_name = row.get("English_name") or existing.english_name
                    existing.category = row.get("Category") or existing.category
                    existing.email = row.get("Email") or existing.email
                    db.session.add(existing)
                else:
                    f = Faculty(
                        korean_name=kname,
                        english_name=row.get("English_name"),
                        category=row.get("Category"),
                        email=row.get("Email")
                    )
                    db.session.add(f)
            db.session.commit()
            flash("Faculty DB uploaded/merged", "success")
            return redirect(url_for("admin_upload_faculty"))
        return render_template("admin_upload.html", target="faculty")

    # enrich excel: user uploads an excel that has only Korean_name and wants enriched file to download
    @app.route("/faculty/enrich", methods=["GET", "POST"])
    def faculty_enrich():
        if request.method == "POST":
            file = request.files.get("file")
            if not file:
                flash("No file", "warning")
                return redirect(url_for("faculty_enrich"))
            bio = enrich_faculty_excel(file, db.session)
            return send_file(
                bio,
                as_attachment=True,
                download_name="faculty_enriched.xlsx",
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        return render_template("faculty_upload_enrich.html")

    @app.route("/faculty/search", methods=["GET"])
    def faculty_search():
        q = request.args.get("q", "").strip()
        results = []
        if q:
            qn = normalize_name(q)
            # exact first
            f = Faculty.query.filter_by(korean_name=qn).first()
            if f:
                results = [{
                    "Korean_name": f.korean_name,
                    "English_name": f.english_name,
                    "Category": f.category,
                    "Email": f.email
                }]
            else:
                # fuzzy: search across all korean_name
                candidates = [row.korean_name for row in Faculty.query.all()]
                fr = fuzzy_search_name(qn, candidates, limit=10)
                for candidate, score, _ in fr:
                    f2 = Faculty.query.filter_by(korean_name=candidate).first()
                    results.append({
                        "Korean_name": f2.korean_name,
                        "English_name": f2.english_name,
                        "Category": f2.category,
                        "Email": f2.email,
                        "score": score
                    })
        return render_template("faculty_search.html", query=q, results=results)

    # ---------- Course: admin upload ----------
    @app.route("/admin/upload/course", methods=["GET", "POST"])
    def admin_upload_course():
        if request.method == "POST":
            pin = request.form.get("admin_pin", "")
            if pin != app.config["ADMIN_PIN"]:
                flash("Admin PIN incorrect", "danger")
                return redirect(url_for("admin_upload_course"))
            file = request.files.get("file")
            if not file:
                flash("No file uploaded", "warning")
                return redirect(url_for("admin_upload_course"))
            res = import_course_excel(file, db.session, CourseModality)
            flash(f"Course import done: {res}", "success")
            return redirect(url_for("admin_upload_course"))
        return render_template("admin_upload.html", target="course")

    # search course by Korean_name or English_name
    @app.route("/course/search", methods=["GET", "POST"])
    def course_search():
        query = request.values.get("q", "").strip()
        results = []
        if query:
            qn = normalize_name(query)
            # exact matches by name
            exacts = CourseModality.query.filter(CourseModality.name == qn).all()
            if exacts:
                results = exacts
            else:
                # fuzzy search across name column
                candidates = [row.name for row in CourseModality.query.all()]
                fr = fuzzy_search_name(qn, candidates, limit=10)
                matched_names = [candidate for candidate, score, _ in fr]
                results = CourseModality.query.filter(CourseModality.name.in_(matched_names)).all()
        return render_template("course_search.html", results=results, query=query)

    # Apply action: expects course id, pin and reason
    @app.route("/course/<int:course_id>/apply", methods=["POST"])
    def course_apply(course_id):
        course = CourseModality.query.get_or_404(course_id)
        pin = request.form.get("pin", "").strip()
        reason = request.form.get("reason", "").strip()
        # First validate pin matches stored row password if exists, otherwise require correct pin from excel? spec: user enters password from existing excel (we store per row)
        # If row has a stored pin, check it. If not stored, reject.
        if not course.password_hash:
            # no row pin; cannot apply
            return jsonify({"ok": False, "message": "No password configured for this entry."}), 400
        from werkzeug.security import check_password_hash
        if not course.check_pin(pin):
            return jsonify({"ok": False, "message": "PIN incorrect"}), 403
        # reason required when new
        if not course.apply_reason and not reason:
            return jsonify({"ok": False, "message": "Reason required"}), 400
        # limit reason length to 1000 unicode chars
        if len(reason) > 1000:
            return jsonify({"ok": False, "message": "Reason too long"}), 400
        course.apply_reason = reason or course.apply_reason
        course.apply_flag = True
        course.modified_date = datetime.now(timezone.utc)
        db.session.add(course)
        db.session.commit()
        return jsonify({"ok": True, "message": "Saved"})

    # Lookup user's submitted info by PIN
    @app.route("/course/<int:course_id>/lookup", methods=["POST"])
    def course_lookup(course_id):
        course = CourseModality.query.get_or_404(course_id)
        pin = request.form.get("pin", "").strip()
        if not course.check_pin(pin):
            return jsonify({"ok": False, "message": "PIN incorrect"}), 403
        # return relevant fields
        data = {
            "No": course.no,
            "Name": course.name,
            "Year": course.year,
            "Semester": course.semester,
            "Language": course.language,
            "Course Title": course.course_title,
            "Time Slot": course.time_slot,
            "Day": course.day,
            "Time": course.time,
            "Frequency(Week)": course.frequency_week,
            "Course format": course.course_format,
            "Apply this semester(Online 70)": "Yes" if course.apply_flag else "No",
            "Reason for Applying": course.apply_reason,
            "Modified Date": course.modified_date.isoformat() if course.modified_date else None
        }
        return jsonify({"ok": True, "data": data})

    # Cancel apply
    @app.route("/course/<int:course_id>/cancel", methods=["POST"])
    def course_cancel(course_id):
        course = CourseModality.query.get_or_404(course_id)
        pin = request.form.get("pin", "").strip()
        if not course.check_pin(pin):
            return jsonify({"ok": False, "message": "PIN incorrect"}), 403
        course.apply_flag = False
        course.modified_date = datetime.now(timezone.utc)
        db.session.add(course)
        db.session.commit()
        return jsonify({"ok": True, "message": "Cancelled"})

    # Admin export all course info (admin PIN)
    @app.route("/admin/export/course", methods=["GET", "POST"])
    def admin_export_course():
        if request.method == "POST":
            pin = request.form.get("admin_pin", "")
            if pin != app.config["ADMIN_PIN"]:
                flash("Admin PIN incorrect", "danger")
                return redirect(url_for("admin_export_course"))
            import pandas as pd
            rows = []
            for c in CourseModality.query.all():
                rows.append({
                    "No": c.no,
                    "Name": c.name,
                    "Year": c.year,
                    "Semester": c.semester,
                    "Language": c.language,
                    "Course Title": c.course_title,
                    "Time Slot": c.time_slot,
                    "Day": c.day,
                    "Time": c.time,
                    "Frequency(Week)": c.frequency_week,
                    "Course format": c.course_format,
                    "Apply this semester(Online 70)": "Yes" if c.apply_flag else "No",
                    "Reason for Applying": c.apply_reason,
                    "Modified Date": c.modified_date.isoformat() if c.modified_date else None
                })
            df = pd.DataFrame(rows)
            bio = BytesIO()
            df.to_excel(bio, index=False, engine="openpyxl")
            bio.seek(0)
            return send_file(bio, as_attachment=True, download_name="course_export.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        return render_template("admin_export.html")

    return app

if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
