import os

from flask import Flask, render_template, url_for

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('settings.cfg', silent=True)
    
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)
    
    # ensure the instance folder exist
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    


    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import game_of_life
    app.register_blueprint(game_of_life.bp)

    

    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/acknowledgement')
    def acknowledgement():
        return render_template('acknowledgement.html')

    return app