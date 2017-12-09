from login import app, db

import sys

from flask import render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from werkzeug.security import generate_password_hash, check_password_hash

#defines User database table structure
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    #use a salted hash for password storage instead of plaintext
    pw_hash = db.Column(db.String(160), nullable=False)

    #defines what is returned when User table is queried
    def __repr__(self):
        return "User: %s" % self.username + ', ' + self.email

    #compares salted hash pw to password, returns T/F
    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

#WTForm for registration, used with register view and register.html
class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    #currently the email validation is only checking string length, but should
    #  restrict to the regex *@*.* where the last * could be further restricted
    #  to a list of all valid domain endings
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        #makes this field required, although the stringfields are also required
        #  as they specify a minimum length
        validators.DataRequired(),
        #checks content to see if it matches the confirm password field
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    #Currently there are no TOS but in the event this app is actually served
    #  it wouldn't be a bad idea to confirm that only test data should be used
    #  and that all emails are fictional and will not be used for any purpose
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])

#basic Form for login page
class LoginForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password')

#register page serves register.html if GET request with register form passed to
#  register.html view
#  With POST request instead creates the new User Object, adds and commits it to the db
#  without commit the change will not persist to the database
@app.route("/register", methods=["GET", "POST"])
def register():
    #Creates a blank registration form to pass to the view
    form = RegistrationForm(request.form)

    #when the POST request is sent the validate function is called which checks
    #  the contents against the validation criteria specified in the form class
    if request.method == 'POST' and form.validate():
        #Creates a User object from the form contents, string validation is handled in the
        #  form class
        user = User(username=form.username.data, email=form.email.data,
                    pw_hash=generate_password_hash(form.password.data))
        #add the user to pending changes to make to the database
        db.session.add(user)
        #save the changes to the database so they persist, generally in larger db
        #  structures you avoid committing as much as possible and instead keep track of
        #  changes in a journal or transaction log which is integrated into the database when
        #  backups are run. This is implemented in SQLAlchemy as db.session.flush() which
        #  writes the pending changes in a transaction log
        db.session.commit()
        flash('Thanks for registering')

        #after submitting redirects user to login page
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

#View displays the db contents, used for testing and verifying objects
#  are being written to the database, if you want to see the full
#  database contents add the missing User properties to User.__repr__
#  return statement
@app.route("/contents")
def db_contents(contents=None):
    #get all User db table records and pass it to the view
    contents=User.query.all()
    return render_template('db_contents.html', contents=contents)

#Login view, GET request serves the login form and POST checks it against
#  the database records.
#  TODO: implement register button/link that directs user to register page,
#        right now they would have to know there is a /register webpage
@app.route("/", methods=["GET", "POST"])
def login():
    #creates a blank login form to pass to the view
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        #Queries the database for the User object with the content of the username field
        #  if no User object is found a 404 page is displayed instead
        db_user = User.query.filter_by(username=form.username.data).first_or_404()

        #Checks the plaintext password string against the salted hash in the db
        login_successful = db_user.check_password(form.password.data)

        #user has auth'd, serve them the website now
        if login_successful:
            return redirect(url_for('successful_login'))

        #This redirects the user to a failed html page if the login is not
        #  successful, however most webapps would remain on the same page and
        #  prompt the user to try again. Can be accomplished in flask by using
        #  the flash() function which will preserve a message over a session and
        #  can be passed to the view
        else:
            return redirect(url_for('failed_login'))
    return render_template('login.html', form=form)

#Page that is served after auth, right now just redirects to the db content page
@app.route("/success")
def successful_login():
    return redirect(url_for('db_contents'))

#TODO: get rid of the fail page and redirect to the login page to have the user
#  attempt to login again. This should be implemented in a reactive way instead of
#  static routing.
@app.route("/fail")
def failed_login():
    return render_template('failed_login.html')
