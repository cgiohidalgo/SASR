# -*- coding: utf-8 -*-

from os.path import join as join_path
from os import makedirs
from flask import Flask


def create_app(test_config=None):
    
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=join_path(app.instance_path, "filer.sqlite"),
    )
    
    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)
    
    try:
        makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)
    
    from . import auth
    app.register_blueprint(auth.bp)
    auth.init_app(app)
    
    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule("/", endpoint="index")
    blog.init_app(app)
    
    from . import files
    app.register_blueprint(files.bp)
    
    return app
