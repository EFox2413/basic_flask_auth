import os.path, tempfile
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

#sets configuration variables, database location, and the secret key (should generally not
#  be published on a public site, but hidden in a file that is excluded from git)
app.config.update(
    DEBUG=True,
    #Note in windows the tempfile directory is in %APPDATA%/../local/temp
    SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(tempfile.gettempdir(), 'test.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SECRET_KEY='secret',
    )

#tells the database which app it is used for
db = SQLAlchemy(app)

#circular reference, of little consequence as we don't actually use it for anything here
#  it's still necessary to ensure the module is imported. A good way to get around this
#  would be through the use of blueprints and application factories as seen in
#  https://github.com/sloria/cookiecutter-flask
import login.views

#creates the database structure if not already present
db.create_all()
