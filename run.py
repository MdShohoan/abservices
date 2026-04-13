# import the create app application factory
#from app import create_app
#from app import app
# import the application config classes
#from config import DevelopmentConfig, ProductionConfig, TestingConfig

#app = create_app()
#app.app_context().push()

#What it does is import the Flask instance called app from app/__init__.py, and call app.run() on it once the script is executed.
import os
#we import waitress here. 
#from waitress import serve
from app import app
#serve(app, host='0.0.0.0', port=5000)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8087)
    #serve(app.app, host='0.0.0.0', port=8080)

#if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=8087)
