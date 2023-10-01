from flask import Blueprint,render_template, request, flash,redirect, url_for,make_response,session
import pickle
from website.config import db
from flask_login import login_user, login_required, logout_user,current_user

auth = Blueprint('auth',__name__)



# Define a function to add no-cache headers to responses
def add_no_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response

# Apply the add_no_cache_headers function to all responses
@auth.after_request
def apply_no_cache(response):
    return add_no_cache_headers(response)

@auth.route('/login', methods=['GET','POST'])
def login():
    next_url = request.args.get('next')
    user = None
    if request.method == 'POST':
        login_role = request.form.get('loginRole')
        password = request.form.get('password')

        if login_role == 'caretaker':
            email = request.form.get('email')
            user = db.verify_login(email = email,id=None)
        elif login_role == 'nurse':
            print("Im here")
            id = request.form.get('employeeID')
            user = db.verify_login(email = None, id = id)
            print(user)

        if user:
            if user.password == password:
                flash("Logged in succesfully")
                login_user(user)
                
                return redirect(next_url or url_for('views.home'))
            else:
                flash('Incorrect password, try again',category="error")
        else:
            flash("Email does not exit.", category="error")
            
    return render_template("login.html")

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))