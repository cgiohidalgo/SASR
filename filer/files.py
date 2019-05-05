# -*- coding: utf-8 -*-

from filer.db import get_db
#from os import scandir, stat
from os.path import join as join_path, isdir, basename, getsize, isfile
from werkzeug.utils import secure_filename
from werkzeug import abort
from re import search
from flask import current_app, Blueprint, request, flash, render_template, redirect, url_for, send_file
from filer.auth import user_required
from mimetypes import guess_type
from re import compile as prepare, IGNORECASE

bp = Blueprint("files", __name__)

def get_files(id):
    cur = get_db().cursor()
    files = [BlogFile(
        join_path(current_app.config["UPLOAD_FOLDER"], row["filename"]),
        counter=row["counter"],
        id=row["id"]
    ) for row in cur.execute(
        """SELECT "id", "filename", "counter" FROM "file" WHERE "post_id" = :pid;""",
        {"pid": id}
    )]
    cur.close()
    return files

def init_app(app):
    app.config.from_mapping(
        UPLOAD_FOLDER=join_path(app.instance_path, "files"),
        UPLOAD_EXTENSIONS=set([
            "mp3", "m3u",
            "pdf"
        ])
    )

def allowed_filename(filename):
    m = search(r"\.(?P<ext>[^.]+)$", filename)
    return m and m["ext"].lower() in current_app.config["UPLOAD_EXTENSIONS"]

#@bp.route("/files")
#@user_required("@admin")
#def index():
#    uf = current_app.config["UPLOAD_FOLDER"]
#    try:
#        files = scandir(uf)
#    except FileNotFoundError:
#        flash("Unable to read upload folder '{:s}'.".format(uf))
#        files = []
#    
#    return render_template("files/index.html", files=files)
#
#@bp.route("/files/upload", methods=("POST",))
#@user_required("@admin")
#def upload():
#    if "file" not in request.files:
#        flash("File is missing.")
#    file = request.files["file"]
#    if file.filename == "":
#        flash("File is missing.")
#    if file and allowed_filename(file.filename):
#        filename = secure_filename(file.filename)
#        filepath = join_path(current_app.config["UPLOAD_FOLDER"], filename)
#        file.save(filepath)
#    else:
#        flash("Bad file or filename '{:s}'.".format(file.filename))
#
#    return redirect(url_for("files.index"))
#
@bp.route("/files/<int:fid>", methods=("GET",))
@user_required()
def download(fid):
    cur = get_db().execute("""SELECT "filename" FROM "file" WHERE "id" = :fid;""", {"fid": fid})
    res = cur.fetchone()
    cur.close()
    
    if res is None:
        abort(404, "There is no file with id {:d}.".format(fid))
    else:
        filename = join_path(current_app.config["UPLOAD_FOLDER"], res["filename"])
        if isfile(filename):
            return send_file(filename, as_attachment=True)
        else:
            abort(404, "The file '{:s}' could not be found.".format(filename))

class BlogFile:
    
    __audio_re = prepare(r"^audio/", IGNORECASE)
    
    def __init__(self, path, counter=None, id=None):
        self.path = path
        self.id = id
        self.counter = counter
        
        if isfile(self.path):
            self.name = basename(self.path)
            self.size = getsize(self.path)
            self.isaudio = self.__audio_re.match(str(guess_type(self.name)[0])) is not None
        else:
            self.name = None
            self.size = None
