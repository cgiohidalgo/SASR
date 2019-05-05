# -*- coding: utf-8 -*-

from flask import Blueprint, flash, g, redirect, render_template, request, url_for, current_app
from werkzeug import abort
from werkzeug.utils import secure_filename
from filer.auth import user_required, authorize_user
from filer.db import get_db, init_db
from filer.files import get_files
from datetime import date, datetime
from os.path import join

bp = Blueprint("blog", __name__)

@bp.route("/")
def index():
    db = get_db()
    #init_db()
    cur = db.execute("""SELECT "id", "title", "body" FROM "post" ORDER BY "id" DESC; """)
    posts = cur.fetchall()
    cur.close()
    
    return render_template("blog/index.html", posts=posts)

@bp.route("/create", methods=("GET", "POST"))
#@user_required("@admin")
def create():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        dt = request.form["date"]
        error = []
        
        if not title:
            error.append("Title must not be empty.")
        if date:
            try:
                dt = datetime.now()
            except ValueError:
                error.append("Date must be given as 'YYYY-MM-DD' or left empty.")
                dt = None
        
        if error:
            flash("\n".join(error))
        else:
            db = get_db()
            cur = db.execute(
                    """
INSERT INTO "post" ("title", "body", "ref_date")
VALUES (:title, :body, :date);
                    """,
                    {"title": title, "body": body, "date": datetime.now() if dt else None}
            )
            db.commit()
            pid = cur.lastrowid

#            flash(len(request.files.getlist("files")))
            add_files(pid, request.files.getlist("files"))
            
            return redirect(url_for(".show", id=pid))
        
    return render_template("blog/create.html")

def add_files(pid, files):
    db = get_db()
    cur = db.cursor()
    for file in files:
        if file.filename:
            try:
                print(">>>>>>>>>>>>>>>>>>>>> ", current_app.config["UPLOAD_FOLDER"])
                
                fname = secure_filename(file.filename)
                file.save(join(current_app.config["UPLOAD_FOLDER"], fname))
                cur.execute(
                    """
INSERT INTO file ("filename", "post_id")
VALUES (:name, :id)
;
                    """,
                    {"id": pid, "name": fname}
                )
                db.commit()
            except:
                flash("Failed to save file '{:s}'.".format(file.filename))

def get_post(id):
    cur = get_db().cursor()
    
    post = cur.execute(
        """
SELECT
    "id",
    "title",
    "body"
FROM "post" p
WHERE "id" = :pid
;
        """,
        {"pid": id}
    ).fetchone()

    cur.close()
    
    if post is None:
        abort(404, "There is no post with id {:d}".format(id))

    return post

@bp.route("/<int:id>/update", methods=("GET", "POST"))
#@user_required("@admin")
def update(id):
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        dt = request.form["date"]
        error = []
        
        if not title:
            error.append("The title must not be empty.")
        if date:
            try:
                dt = datetime.now()
            except ValueError:
                error.append("Date must be given as 'YYYY-MM-DD' or left empty.")
                dt = None
        
        if error:
            flash("\n".join(error))
        else:
            db = get_db()
            db.execute(
                """
                UPDATE "post"
                SET
                    "title" = :title,
                    "body" = :body,
                    "ref_date" = :date
                WHERE "id" = :pid;""",
                {"title": title, "body": body, "date": datetime.now() if dt else None, "pid": id}
            ).close()
            db.commit()

            add_files(id, request.files.getlist("files"))
            
            return redirect(url_for(".show", id=id))
    
    return render_template("blog/update.html", post=get_post(id), files=get_files(id))

@bp.route("/<int:id>/delete", methods=("POST",))
#@user_required("@admin")
def delete(id):
#    get_post(id)
    db = get_db()
    db.execute("""DELETE FROM "post" WHERE "id" = :pid;""", {"pid": id}).close()
    db.commit()
    return redirect(url_for("blog.index"))

@bp.route("/<int:id>", methods=("GET",))
#@user_required()
def show(id):
    return render_template("blog/post.html", post=get_post(id), files=get_files(id))

def init_app(app):
    app.config.from_mapping(
        UPLOAD_FOLDER=join(app.instance_path, "files"),
        UPLOAD_EXTENSIONS=set([
            "mp3", "m3u",
            "pdf"
        ])
    )
