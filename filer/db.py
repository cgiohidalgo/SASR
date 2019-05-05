# -*- coding: utf-8 -*-

from sqlite3 import connect, PARSE_DECLTYPES, Row
from flask import current_app, g
from flask.cli import with_appcontext
from click import command, echo

def get_db():
    if "db" not in g:
        g.db = connect(
            current_app.config["DATABASE"],
            detect_types=PARSE_DECLTYPES,
        )
        g.db.row_factory = Row
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    
    if db is not None:
        db.close()
        
def init_db():
    db = get_db()
    with current_app.open_resource("schema.sql") as schema_file:
        db.executescript(schema_file.read().decode("utf8"))

@command("init-db")
@with_appcontext
def init_db_command():
    """(Re-)Initialize the application database."""
    init_db()
    echo("Database initialized.")

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
