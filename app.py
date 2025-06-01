from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
import json
import random
import requests
from datetime import datetime
from dotenv import load_dotenv
import os
import re 

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('secret_key')

load_dotenv()
token = os.getenv('token')
pixela_endpoint = os.getenv('pixela_endpoint')

db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')

db.init_app(app)

# Configure Flask-Login's Login Manager
login_manager = LoginManager()
login_manager.init_app(app)

# Create a user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

# CREATE TABLE IN DB

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    habit = db.Column(db.String(1000))


with app.app_context():
    db.create_all()

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template("login.html", logged_in=current_user.is_authenticated)

def generate_pixela_username(email):
    # Lowercase and replace invalid email characters
    username = email.lower().replace('@', 'b').replace('.', 'a')

    # Remove anything that's not a-z, 0-9, or -
    username = re.sub(r'[^a-z0-9-]', '', username)

    # Ensure it starts with a letter
    if not username[0].isalpha():
        username = 'a' + username

    # Limit length to 33 characters (Pixela limit)
    return username[:33]

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method=="POST":
        with open('quotes.json') as f:
            quotes = json.load(f)
        random_quote = random.choice(quotes)

        email= request.form['email']
        password= request.form['password']
        habit=request.form['habit']

        # Find user by email entered.
        result= db.session.execute(db.select(User).where(User.email == email))
        user=result.scalar()
        if user:
            flash("user with this email already exists.")
            return redirect(url_for('home'))
        

        # Hashing and salting the password entered by the user 
        hashed_and_salted_pw=generate_password_hash(
            request.form['password'],
            method='pbkdf2:sha256',
            salt_length=8
        )

        # Storing the hashed password in our database
        new_User = User (
            name=request.form['name'],
            email=request.form['email'],
            password=hashed_and_salted_pw,
            habit=request.form['habit']
        )
        db.session.add(new_User)
        db.session.commit()

        print("Email:", email)
        print("User found:", user)
        print("All users:", User.query.all())

        # Create Pixela user and graph
        success, username, graph_id = create_pixela_user_and_graph(email, habit)
        if success:
            print("graph made ")
            return render_template("index.html", username=username, habit=habit, graph_id=graph_id, quote=random_quote)
        else:
            flash("User registered but graph creation failed.")
            return redirect(url_for('home'))

        # return redirect(url_for('login'))
    
    return render_template('login.html')
    
@app.route('/login', methods=["GET","POST"])
def login():

    with open('quotes.json') as f:
        quotes = json.load(f)
    random_quote = random.choice(quotes)

    if request.method=="POST":
        email= request.form['email']
        password= request.form['password']


        # Find user by email entered.
        result= db.session.execute(db.select(User).where(User.email == email))
        user=result.scalar()
        
        #email doesnt exist
        if not user:
            flash ("Email does not exist. please try again")
            return redirect(url_for("home"))
        #password is wrong
        elif not check_password_hash(user.password, password):
            flash("password isnt correct please try again")
            return redirect(url_for("home"))
        #login is sucessful
        else:
            login_user(user)
            username = generate_pixela_username(email)
            habit = user.habit
            return render_template("index.html", logged_in=True, quote=random_quote, username=username, habit=habit, graph_id="graph1")

    return render_template("login.html")


def create_pixela_user_and_graph(email,habit):
        username = generate_pixela_username(email)

        user_params = {
        "token": token,
        "username": username,
        "agreeTermsOfService": "yes",
        "notMinor": "yes",
        }

        create_account_response = requests.post(url="https://pixe.la/v1/users", json=user_params)
        print(create_account_response.text)

        # STEP2: CREATE GRAPH
        graph_id = "graph1"
        graph_config = {
            "id": graph_id,
            "name": habit,
            "unit": "times",
            "type": "int",
            "color": "kuro",
            "timezone": "Asia/Kolkata",
            "isSecret": False,
            "publishOptionalData": False
        }

        graph_endpoint = f"https://pixe.la/v1/users/{username}/graphs"

        headers = {
            "X-USER-TOKEN": token
        }
        graph_response = requests.post(graph_endpoint, json=graph_config, headers=headers)


        print("USER RESPONSE:", create_account_response.text)
        print("GRAPH RESPONSE:", graph_response.text)

        if graph_response.status_code == 200:
            return True, username, graph_id
        else:
            return False, None, None
        
        
@app.route("/submit", methods=["POST"])
def submit():
    if request.method=="POST":
        quantity = request.form["quantity"]
        email = request.form["email"]

        graph_id = "graph1"
        user_email = current_user.email
        username = generate_pixela_username(email)

        post_endpoint = f"{pixela_endpoint}/{username}/graphs/{graph_id}"

        headers = {
            "X-USER-TOKEN": token
        }
        today = datetime.now()

        color_param = {
            "date": today.strftime("%Y%m%d"),
            "quantity": quantity,
        }
        pixel_color_response = requests.post(url=post_endpoint, json=color_param, headers=headers)

        if pixel_color_response.status_code == 200:
            flash("Habit updated successfully.")
            return redirect(url_for('index'))
        else:
            flash(f"Error submitting habit: {pixel_color_response.text}")
            return redirect(url_for('index'))
        

@app.route('/index')
@login_required
def index():
    print(current_user.name)
    print(current_user.habit)
    email = request.form["email"]
    with open('quotes.json') as f:
        quotes = json.load(f)
    random_quote = random.choice(quotes)
    username = generate_pixela_username(email)
    habit = current_user.habit
    # user_graph_id = f"graph_{current_user.id}"
    return render_template('index.html', logged_in=current_user.is_authenticated, quote=random_quote, username=username, habit=habit, graph_id="graph1")

@app.route('/reset',methods=["POST"])
def reset():
    """Clear session (for testing)"""
    current_user.is_authenticated == False
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)