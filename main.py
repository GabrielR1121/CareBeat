from website import create_app
from website.config import config
"""
Running this file will launch the server and start the flask application.
This application was created by Gabriel E. Rodriguez Garcia.
The purpose of this application is to Help nursing homes and doctors better communicate about the treatment of patients
This Project is being made for my Mini-Thesis class SICI-4038 at the Univesity of Puerto Rico at Bayamon.
"""

app = create_app()


if __name__ == '__main__':
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)

   