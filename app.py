from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)
Session(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)

with app.app_context():
    db.create_all()

def check_password_requirements(password):
    errors = []
    if not any(c.islower() for c in password):
        errors.append('It must contain a lowercase letter')
    if not any(c.isupper() for c in password):
        errors.append('It must contain an uppercase letter')
    if not password[-1].isdigit():
        errors.append('It must end in a number')
    if len(password) < 8:
        errors.append('Password should be at least 8 characters')
    return errors

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('secret'))
        else:
            return render_template('report.html', errors=['Invalid username or password'])
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        
        password_errors = check_password_requirements(password)
        errors = []
        if password != confirm_password:
            errors.append('Passwords do not match')
            return render_template('report.html', errors=errors)
        elif User.query.filter_by(email=email).first():
            errors.append('Email address is already registered')
            return render_template('report.html', errors=errors)
        elif password_errors:
            return render_template('report.html', errors=password_errors)
        else:
            new_user = User(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('thankyou'))
    return render_template('signup.html')

@app.route('/secret')
def secret():
    if 'user_id' in session:
        return render_template('secretPage.html')
    return redirect(url_for('index'))

@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')

@app.route('/report')
def report():
    return render_template('report.html')

if __name__ == '__main__':
    app.run(debug=True)
