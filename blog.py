from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

#User Registration Form
class RegisterForm(Form):

    #name must have minimum 4 and maximum 25 characters
    name = StringField("Name Surname", validators=[validators.Length(min=4, max=25)])
    #username must have minimum 5 and maximum 35 characters
    username = StringField("Username", validators=[validators.Length(min=5, max=35)])
    #email must be in a valid form
    email = StringField("Email", validators=[validators.Email(message="Please enter a valid email address...")])
    #entering a password must be mandatory and the password must match the one to be entered in the confirm field
    password = PasswordField("Password", validators=[validators.DataRequired(message="Please set a password..."),
                                                     validators.EqualTo(fieldname="confirm", message="Password does not match")])
    confirm = PasswordField("Confirm Password")

#define and config the Flask app
app = Flask(__name__)
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "bkbblog"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

#create a MySQL object for database connection
mysql = MySQL(app)

#Homepage
@app.route("/")
def index():

    #return index template as response
    return render_template("index.html")

#about page
@app.route("/about")
def about():

    #return about page as response
    return render_template("about.html")


if __name__ == "__main__":

    app.run(debug=True)