import os

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__)) + '/database/'

# Enable debug mode.
DEBUG = True

# Secret key for session management. You can generate random strings here:
# https://randomkeygen.com/
SECRET_KEY = 'my precious'

UPLOAD_FOLDER = 'flask-app/uploads'

# Connect to the database
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

