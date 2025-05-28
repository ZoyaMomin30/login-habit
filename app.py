from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'averyverysecretkey'

# CREATE DATABASE
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(model_class=Base)
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
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))
    habit: Mapped[str] = mapped_column(String(1000))


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    return render_template("index.html", logged_in=current_user.is_authenticated)

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method=="POST":
        email= request.form['email']
        password= request.form['password']

        # Find user by email entered.
        result= db.session.execute(db.select(User).where(User.email == email))
        user=result.scalar()
        if user:
            flash("user with this email already exists.")
            return redirect(url_for('login'))
        

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

        return redirect(url_for('page'))
    
    return render_template('page.html', logged_in=current_user.is_authenticated)
    
@app.route('/login', methods=["GET","POST"])
def login():
    if request.method=="POST":
        email= request.form['email']
        password= request.form['password']

        # Find user by email entered.
        result= db.session.execute(db.select(User).where(User.email == email))
        user=result.scalar()

        #email doesnt exist
        if not user:
            flash ("Email doest exist. please try again")
            return redirect(url_for("home"))
        #password is wrong
        elif not check_password_hash(user.password, password):
            flash("password isnt correct please try again")
            return redirect(url_for("home"))
        #login is sucessful
        else:
            login_user(user)
            return redirect(url_for("page"))

    return render_template("index.html", logged_in=current_user.is_authenticated)


@app.route('/page')
@login_required
def page():
    print(current_user.name)
    print(current_user.habit)
    return render_template('page.html', logged_in=True)


if __name__ == "__main__":
    app.run(debug=True)
