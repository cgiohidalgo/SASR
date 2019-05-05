# -*- coding: utf-8 -*-

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from flask.cli import AppGroup
from werkzeug.security import check_password_hash, generate_password_hash
from filer.db import get_db
from functools import wraps
from click import argument, echo, prompt, confirm
from sqlite3 import Error as SQLiteError

bp = Blueprint("auth", __name__, url_prefix="/auth")
@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = []
        
        if not username:
            error.append("Username must not be empty")
        if not password:
            error.append("Password must not be empty")
        
        cur = db.execute(
            """SELECT "id" FROM "user" WHERE "username" = :user;""",
            {"user": username}
        )
        if cur.fetchone() is not None:
            error.append("User {:s} is already registered.".format(username))
        cur.close()
        
        if error:
            flash("\n".join(error))
        else:
            db.execute(
                """INSERT INTO "user" ("username", "password") VALUES (:user, :pass);""",
                {"user": username, "pass": generate_password_hash(password)}
            ).close()
            db.commit()
            return redirect(url_for("auth.login"))
    
    return render_template("auth/register.html")

@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = []
        
        cur = db.execute(
            """SELECT "id", "password" FROM "user" WHERE "username" = :user;""",
            {"user": username}
        )
        user = cur.fetchone()
        cur.close()
        
        if user is None:
            error.append("User '{:s}' does not exist.".format(username))
        elif not check_password_hash(user["password"], password):
            error.append("Bad password for user '{:s}'.".format(username))
        else:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))
        
        flash("\n".join(error))
    
    return render_template("auth/login.html")

@bp.before_app_request
def load_authed_user():
    user_id = session.get("user_id")
    
    if user_id is None:
        g.user = None
        g.groups = []
    else:
        cur = get_db().cursor()
        
        g.user = cur.execute(
            """SELECT "id", "username" FROM "user" WHERE "id" = :uid;""",
            {"uid": user_id}
        ).fetchone()
        
        g.groups = [r["groupname"] for r in cur.execute(
            """
SELECT "groupname"
FROM "group", "user_in_group" uig
WHERE 1
    AND "id" = uig."group_id"
    AND uig."user_id" = :uid
;
            """,
            {"uid": user_id}
        ).fetchall()]
        
        cur.close()

@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

def authorize_user(user):
    if g.user is None:
        return False
    else:
        if isinstance(user, (list, tuple)):
            return any(authorize_user(u) for u in user)
        
        authed = False
        if user[0] == '@':
            cur = get_db().execute(
                """
SELECT
    g."id"
FROM
    "group" g,
    "user_in_group" uig
WHERE 1
    AND g."groupname" = :group
    AND uig."user_id" = :uid
    AND g."id" = uig."group_id"
;
                """,
                {"group": user[1:], "uid": g.user["id"]}
            )
            if cur.fetchone() is not None:
                authed = True
            cur.close()
        elif user == g.user["username"]:
            authed = True

        return authed

def user_required(user=None):
    def dec(view):
        @wraps(view)
        def wrapped_view(**kwargs):
            authed = g.user is not None if user is None else authorize_user(user)
            return view(**kwargs) if authed else redirect(url_for("auth.login"))
        return wrapped_view
    return dec

user_cli = AppGroup("user")

@user_cli.command("create")
@argument("name")
@argument("group", required=False)
def create_user_command(name, group=None):
    """Create a new user."""
    db = get_db()
    cur = db.execute("BEGIN TRANSACTION;")
    
    if cur.execute(
        """SELECT "id" FROM "user" WHERE "username" = :name;""",
        {"name": name}
    ).fetchone() is not None:
        echo("User '{:s}' does already exist.".format(name))
        cur.close()
        return
    
    if group is None:
        group_id = None
    else:
        group_res = cur.execute(
            """SELECT "id" FROM "group" WHERE "groupname" = :name;""",
            {"name": group}
        ).fetchone()
        if group_res is None:
            if confirm("Group '{:s}' does not exist. Create it?".format(group), default=True):
                try:
                    cur.execute(
                        """INSERT INTO "group" ("groupname") VALUES (:name);""",
                        {"name": group}
                    )
                except SQLiteError as err:
                    echo("Failed to create group '{:s}': {:s}".format(group, err.args[0]))
                    cur.execute("ROLLBACK TRANSACTION;")
                    cur.close()
                    return
                group_id = cur.lastrowid
            else:
                echo("I did not create user '{:s}'.".format(name))
                cur.close()
                return
        else:
            group_id = group_res["id"]
    
    while True:
        password = prompt("Enter a password for user '{:s}'".format(name), hide_input=True, type=str)
        if len(password) > 5:
            break
        echo("Password not acceptable, too short.")
    
    try:
        cur.execute(
            """INSERT INTO "user" ("username", "password") VALUES (:name, :secret);""",
            {"name": name, "secret": generate_password_hash(password)}
        )
        if group_id is not None:
            cur.execute(
                """INSERT INTO "user_in_group" ("user_id", "group_id") VALUES (:uid, :gid);""",
                {"uid": cur.lastrowid, "gid": group_id}
            )
        cur.execute("COMMIT TRANSACTION;")
    except SQLiteError as err:
        echo("Failed to create user '{:s}': {:s}".format(name, err.args[0]))
        cur.execute("ROLLBACK TRANSACTION;")
        cur.close()
        return
    
    if group_id is None:
        echo("User '{:s}' created.".format(name))
    else:
        echo("User '{:s}' created as member of group '{:s}'.".format(name, group))

group_cli = AppGroup("group")

@group_cli.command("create")
@argument("name")
def create_group_command(name):
    """Create new user group."""
    db = get_db()
    cur = db.execute(
        """SELECT "id" FROM "group" WHERE "groupname" = :name;""",
        {"name": name}
    )
    
    if cur.fetchone() is not None:
        echo("Group '{:s}' does already exist.".format(name))
        cur.close()
        return
    
    try:
        db.execute(
            """INSERT INTO "group" ("groupname") VALUES (:name);""",
            {"name": name}
        ).close()
        db.commit()
    except SQLiteError as err:
        echo("Failed to create group '{:s}': {:s}".format(name, err.args[0]))
        return
    
    echo("Group '{:s}' created.".format(name))

def init_app(app):
    app.cli.add_command(user_cli)
    app.cli.add_command(group_cli)
    app.context_processor(lambda: {"auth": authorize_user})
