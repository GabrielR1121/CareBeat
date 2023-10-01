from flask import Flask
from flask_session import Session
from flask_login import LoginManager
from website.config import db



def create_app():
    '''
    This is the starting method of the flask application. All the flask BASIC configurations are done here
    '''
    app = Flask(__name__)
    #This secret key will eventually change so its not visible to everyone on github
    app.config['SECRET_KEY'] = 'QWERTY'

    #Imports the views file and registers the routes inside the application
    from .views import views
    from .auth import auth

    app.register_blueprint(views,url_prefix="/")
    app.register_blueprint(auth,url_prefix="/")

    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_KEY_PREFIX'] = 'your_session_prefix'
    Session(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        user_data = db.get_caretaker(id)
        if user_data:
            return user_data
        else:
            return db.get_nurse(id) 

    return app