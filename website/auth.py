from flask import Blueprint,render_template, request, flash,redirect, url_for
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
        #Receive role and password from submitted HTML Form
        login_role = request.form.get('loginRole')
        password = request.form.get('password')
        
        #If the role is caretaker
        if login_role == 'caretaker':
            #Retrieve the email
            email = request.form.get('email')
            #Validate the data
            user = db.verify_login(email = email,id=None)

            #Else if User role is nurse
        elif login_role == 'nurse':
            #Retrieve Employee Id
            id = request.form.get('employeeID')
            #Validate Data
            user = db.verify_login(email = None, id = id)

        if user:
            if user.password == password:
                flash("Logged in succesfully")
                #Method used internally in Flask-Login Library to login user
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