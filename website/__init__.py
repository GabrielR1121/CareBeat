from flask import Flask

def create_app():
    '''
    This is the starting method of the flask application. All the flask BASIC configurations are done here
    '''
    app = Flask(__name__)
    #This secret key will eventually change so its not visible to everyone on github
    app.config['SECRET_KEY'] = 'QWERTY'

    #Imports the views file and registers the routes inside the application
    from .views import views
    app.register_blueprint(views,url_prefix="/")

    return app