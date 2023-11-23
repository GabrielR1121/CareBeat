from flask import Flask
from flask_session import Session
from flask_login import LoginManager
from website.config import db, config


def create_app():
    '''
    This is the starting method of the flask application. All the flask BASIC configurations are done here
    '''
    app = Flask(__name__)

    

    #Imports the views file and registers the routes inside the application
    from .views import views
    from .auth import auth

    app.register_blueprint(views,url_prefix="/")
    app.register_blueprint(auth,url_prefix="/")

    #Creates a secure key to store the session under
    app.config['SECRET_KEY'] = config.SECRET_KEY

    #Session configurations to make sure session data is handled correctly
    app.config['SESSION_TYPE'] = config.SESSION_TYPE
    app.config['SESSION_PERMANENT'] = config.SESSION_PERMANENT
    app.config['SESSION_USE_SIGNER'] = config.SESSION_USE_SIGNER
    app.config['SESSION_KEY_PREFIX'] = config.SESSION_KEY_PREFIX
    Session(app)

    #Creates an instance of the flask login to pass to the application
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    #After the user is autheticated the user is loaded to the flask session with all of their info
    @login_manager.user_loader
    def load_user(id):
        user_data = db.get_caretaker(id)
        if user_data:
            return user_data
        else:
            return db.get_nurse(id) 

    return app