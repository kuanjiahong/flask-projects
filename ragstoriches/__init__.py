import os

from flask import Flask, render_template

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if app.config["ENV"] == 'production':
        app.config.from_pyfile('prod_settings.cfg')
    elif app.config["ENV"] == 'development':
        app.config.from_pyfile('dev_settings.cfg')
    
    if test_config is not None:
        # load the test config if passed in
        app.config.from_pyfile('testing_settings.cfg')
    
    # ensure the instance folder exist
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    
    from . import auth
    app.register_blueprint(auth.bp)

    from . import game_of_life
    app.register_blueprint(game_of_life.bp)
    
    @app.route('/acknowledgement')
    def acknowledgement():
        return render_template('acknowledgement.html')

    return app