from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
from helpers import apology, login_required

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///messdb.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def get_index():
    """Show list of shortcuts"""
    userid = session["user_id"]

    if userid == 1:
        return redirect("/status")
    else:
        return redirect("/absent")

@app.route("/status")
@login_required
def status():

    rows = db.execute("SELECT * FROM users WHERE status=?",'Absent')
    veg_row = db.execute("SELECT * FROM users WHERE meal=?",'veg')
    non_veg_row = db.execute("SELECT * FROM users WHERE meal=?",'non_veg')
    
    veg_count = len(veg_row)
    non_veg_count = len(non_veg_row)
    total_count= veg_count + non_veg_count
    return render_template("status.html", rows=rows, total_count=total_count,veg_count=veg_count, non_veg_count=non_veg_count)

@app.route("/absent", methods=["GET", "POST"])
# @login_required
def absent():

    if request.method == "POST":
        # Ensure email was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for email
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure email exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # # Remember which user has logged in
        # session["user_id"] = rows[0]["id"]

        db.execute("UPDATE users SET status=? WHERE username=? ","Absent", rows[0]["username"])

        #flash welcome message
        # flash("Absense Recorded!")

        return redirect("/success")

    else:
        return render_template("absent.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        if not request.form.get("email"):
            return apology("must provide email", 400)

        elif not request.form.get("password"):
            return apology("must provide password", 400)

        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation", 400)

        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("password and confirmation do not match", 400)
        
        # Query database for username and email
        email_rows = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))
        username_rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("email"))

        meal = request.form.get("meal")

        # Ensure username exists
        if len(username_rows) == 1:
            return apology("Username already exists", 400)
        
        # Ensure email exists
        if len(email_rows) == 1:
            return apology("Email already exists", 400)
        
        #get date
        data = datetime.datetime.now()
        today_date = str(data.date())

        print(request.form.get("meal"))
        
        # adding data into the database
        db.execute("INSERT INTO users(email, hash, meal, username, date) VALUES(?, ?, ?, ?, ?)", request.form.get("email"), generate_password_hash(request.form.get("password")), request.form.get("meal"), request.form.get("username"), today_date)

        rows1 = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))
        # Remember which user has logged in
        session["user_id"] = rows1[0]["id"]

        # #flash welcome message
        # flash("Absense Recorded!")

        return redirect("/")
    
    else:
         return render_template("signup.html")
    
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure email was submitted
        if not request.form.get("username"):
            return apology("must provide email", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for email
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure email exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # name = rows[0]["username"]

        # #flash welcome message
        # flash(f"Welcome Back, {name} !")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    
@app.route("/success")
def success():
    return render_template("success.html")
if __name__ == '__main__':
    app.run(debug=True)

    
