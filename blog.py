from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

#login decorator for pages or processes that require login
def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "logged_in" in session:
            
            #return function if logged in
            return f(*args, **kwargs)
        
        else:
            
            #flash a denger message if not logged in
            flash("Please login first.", "danger")

            #return login page
            return redirect(url_for("login"))
    
    return decorated_function

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

#article form
class ArticleForm(Form):

    #title field
    title = StringField("Article Title", validators=[validators.Length(min=5, max=100)])
    #content field
    content = TextAreaField("Article Content", validators=[validators.Length(min=10)])

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

#articles page
@app.route("/articles")
def articles():

    #define a cursor for database operations
    cursor = mysql.connection.cursor()

    #define the query to select data
    query = "SELECT * FROM articles"

    #execute query and set it to the result variable
    result = cursor.execute(query)

    if result > 0:
        
        #if there are articles, get their data
        articles = cursor.fetchall()

        #return the articles page with articles
        return render_template("articles.html", articles = articles)

    else:

        #if there are no articles, return the articles page with an appropriate error
        return render_template("articles.html")

#dashboard page
@app.route("/dashboard")
#call the login_required decorator
@login_required
def dashboard():

    #defina a cursor for database connections
    cursor = mysql.connection.cursor()

    #define the query for select data by author
    query = "SELECT * FROM articles WHERE author = %s"

    #execute the query by using the logged in user as author
    result = cursor.execute(query, (session["username"],))

    if result > 0:

        #if there are articles, get their data
        articles = cursor.fetchall()

        #return the dashboard page with user's articles
        return render_template("dashboard.html", articles = articles)
    
    else:
        
        #if there are no articles, return the articles page with an appropriate error
        return render_template("dashboard.html")

#register page
@app.route("/register", methods = ["GET", "POST"])
def register():

    #create object from RegisterForm class and request a form suitable for the RegisterForm class
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

    #create object from LoginForm class and request a form suitable for the LoginForn class
    form = LoginForm(request.form)

    #check if the request is post 
    if request.method == "POST":
        
        #get data from the form
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

                #open a session
                session["logged_in"] = True
                session["username"] = username
                
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
    
#article detail page
@app.route("/article/<string:id>")
def detail(id):
    
    #create a cursor for database operations
    cursor = mysql.connection.cursor()

    #define the query to select data by id
    query = "SELECT * FROM articles WHERE id = %s"

    #execute query and set it to result variable
    result = cursor.execute(query, (id,))

    if result > 0:
        
        #if the article exists get its data
        article = cursor.fetchone()

        #return detail page with article
        return render_template("detail.html", article = article)

    else:
        
        #if the article not exist, return detail page with an appropriate warning 
        return render_template("detail.html")
    
#logout
@app.route("/logout")
def logout():

    #clear the session
    session.clear()

    #return homepage
    return redirect(url_for("index"))

#article adding page
@app.route("/addarticle", methods = ["GET", "POST"])
def addarticle():

    #create object from ArticleForm class and request a form suitable for the ArticleForm class
    form = ArticleForm(request.form)

    #check if the request is post and validate the form
    if request.method == "POST" and form.validate():

        #get data from the form
        title = form.title.data
        content = form.content.data
        
        #define a cursor for database connection
        cursor = mysql.connection.cursor()

        #define the query to insert data
        query = "INSERT INTO articles(title, author, content)  VALUES(%s, %s, %s)"

        #execute the query by using logged in user as author
        cursor.execute(query, (title, session["username"], content))

        #commit changes
        mysql.connection.commit()

        #close the cursor
        cursor.close()

        #flash a success message if the article addition was successful
        flash("Article has been successfully added.", "success")

        #return the dashboard page
        return redirect(url_for("dashboard"))
    
    else:
        
        #if the request is get return the addarticle page with form
        return render_template("addarticle.html", form = form)
    
#edit article
@app.route("/edit/<string:id>", methods = ["GET", "POST"])
#call the login_required decorator
@login_required
def edit(id):

    if request.method == "GET":
        
        #create a cursor for database operations
        cursor = mysql.connection.cursor()

        #define the query to select data by author and id
        query = "SELECT * FROM articles WHERE author = %s AND id = %s"

        #execute the query and set it to result variable by using logged in user as author
        result = cursor.execute(query, (session["username"], id))

        if result > 0:
            
            #if the article exists, get its data
            article = cursor.fetchone()

            #create a form object from ArticleForm
            form = ArticleForm()

            #set current data of the article to the form
            form.title.data = article["title"]
            form.content.data = article["content"]

            #if the method is get, return edit page with form that includes current data of the article
            return render_template("edit.html", form = form)

        else:
            
            #flash a danger message if the article not exist or the article does not belong to the logged in user
            flash("No such article exists or you are not authorised to edit this article.", "danger")

            #return homepage
            return redirect(url_for("index"))

    else:
        
        #create object from ArticleForm class and request a form suitable for the ArticleForm class
        form = ArticleForm(request.form)

        #get data from the form
        new_title = form.title.data
        new_content = form.content.data

        #create a cursor for database operations
        cursor = mysql.connection.cursor()
        
        #define the query to update article by id
        query2 = "UPDATE articles SET title = %s, content = %s WHERE id = %s"

        #execute the query
        cursor.execute(query2, (new_title, new_content, id))

        #commit changes
        mysql.connection.commit()

        #close the cursor
        cursor.close()

        #flash a success message if update is successful
        flash("The article has been successfully edited.", "success")

        #return the dashboard page
        return redirect(url_for("dashboard"))
    
#delete article
@app.route("/delete/<string:id>")
#call the login_required decorator
@login_required
def delete(id):

    #create a cursor for database operations
    cursor = mysql.connection.cursor()

    #define the query to select data by author and id
    query = "SELECT * FROM articles WHERE author = %s AND id = %s"

    #execute the query and set it to result variable
    result = cursor.execute(query, (session["username"], id))

    if result > 0:
        
        #define the query2 to delete data by id
        query2 = "DELETE FROM articles WHERE id = %s"

        #execute the query2
        cursor.execute(query2, (id,))

        #commit changes
        mysql.connection.commit()

        #close the cursor
        cursor.close()

        #return the dashboard page
        return redirect(url_for("dashboard"))

    else:
        
        #flash a danger message if the article not exist or the article does not belong to the logged in user
        flash("No such article exists or you are not authorised to delete this article.", "danger")

        #return to homepage
        return redirect(url_for("index"))
    
#search
@app.route("/search", methods = ["GET", "POST"])
def search():

    if request.method == "GET":
        
        #if the method is get, return to homepage
        return redirect(url_for("index"))
    
    else:

        #get input data from form
        keyword = request.form.get("keyword")

        #create a cursor for database operations
        cursor = mysql.connection.cursor()

        #define the query to select data by title and keyword(i.e input data from form)
        query = "SELECT * FROM articles WHERE title LIKE '%" + keyword + "%' "

        #execute the query
        result = cursor.execute(query)

        if result > 0:
            
            #if articles exist, get their data
            articles = cursor.fetchall()

            #if the method is post, return the articles page with found articles
            return render_template("articles.html", articles = articles)

        else:
            
            #flash a warning message if there are no articles found
            flash("No suitable articles found.", "warning")

            #return the articles page
            return redirect(url_for("articles"))

if __name__ == "__main__":

    app.run(debug=True)