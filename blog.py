from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

#user registration form
class RegisterForm(Form):

    #name must have minimum 4 and maximum 25 characters
    name = StringField("Name Surname", validators=[validators.Length(min=4, max=25, 
                                                                     message="Name must be at least 4 and no more than 25 characters long.")])
    #username must have minimum 5 and maximum 35 characters
    username = StringField("Username", validators=[validators.Length(min=5, max=35,
                                                                    message="Username must be at least 5 and no more than 35 characters long.")])
    #email must be in a valid form
    email = StringField("Email", validators=[validators.Email(message="Please enter a valid email address.")])
    #entering a password must be mandatory and the password must match the one to be entered in the confirm field
    password = PasswordField("Password", validators=[validators.DataRequired(message="Please set a password."),
                                                     validators.EqualTo(fieldname="confirm", message="Password does not match.")])
    confirm = PasswordField("Confirm Password")

#user login form
class LoginForm(Form):

    #username field
    username = StringField("Username")
    #password field
    password = PasswordField("Password") 

#define the Flask app
app = Flask(__name__)

#set a secret key for flash messages
app.secret_key = "bkbblog"

#MySQL configuraitons
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "bkbblog"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

#create a MySQL object for database connection
mysql = MySQL(app)

#homepage
@app.route("/")
def index():

    #return index template as response
    return render_template("index.html")

#about page
@app.route("/about")
def about():

    #return about page as response
    return render_template("about.html")

#register page
@app.route("/register", methods = ["GET", "POST"])
def register():

    #create object from RegisterForm class and if the request is post, put all the information in 'form' into 'RegisterForm'.
    form = RegisterForm(request.form)

    #check if the request is post and validate the form
    if request.method == "POST" and form.validate():

        #get data from the form, hash the password
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(form.password.data)

        #create a cursor for database operations
        cursor = mysql.connection.cursor()

        #define the query to insert data
        query = "INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)"

        #execute the query 
        cursor.execute(query, (name, email, username, password))

        #commit changes
        mysql.connection.commit()

        #close the cursor
        cursor.close()

        #flash a success message if registration is successful
        flash("You have successfully registered.", "success")
        
        #go to the url related to the specified function when post is made
        return redirect(url_for("login"))
    
    else:
        
        #return register page with form if the request is get
        return render_template("register.html", form = form)
    
#login page
@app.route("/login", methods = ["GET", "POST"])
def login():

    form = LoginForm(request.form)

    if request.method == "POST":
        
        #get data from the dorm
        username = form.username.data
        entered_password = form.password.data

        #create a cursor for database operations
        cursor = mysql.connection.cursor()

        #define the query to select data by username
        query = "SELECT * FROM users WHERE username = %s"

        #execute query and set it to the result variable
        result = cursor.execute(query, (username,))

        if result > 0:
            
            #if the user exists get its data
            data = cursor.fetchone()

            #get user's password
            real_password = data["password"]

            #check whether the password entered by the user and the password in the database are equal
            if sha256_crypt.verify(entered_password, real_password):
                
                #flash a success message if passwords are equal
                flash("You have successfully logged in.", "success")
                
                #return homepage
                return redirect(url_for("index"))
            
            else:

                #flash a danger message if passwords are not equal
                flash("Wrong password.", "danger")

                #return login page
                return redirect(url_for("login"))

        else:
            
            #flash a danger message if the user not exist
            flash("User does not exist.", "danger")
            
            #return login page
            return redirect(url_for("login"))
    else:
        
        #return login page with form if the request is get
        return render_template("login.html", form = form)

if __name__ == "__main__":

    app.run(debug=True)