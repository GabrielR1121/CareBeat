from flask import Blueprint, render_template, session,request,redirect,url_for
from flask_login import  login_required,current_user
import json
import plotly
import pickle
from . import dash
from website.config import db

views = Blueprint('views', __name__)

#Gets Selected Resident from the pickle in the session
def get_selected_resident():
    selected_resident_data = session.get('selected_resident')
    if selected_resident_data:
        return pickle.loads(selected_resident_data)
    return None

#Gets the Selected Medication from the pickle in the session
def get_selected_medication():
    selected_medication_data = session.get('selected_medication')
    if selected_medication_data:
        return pickle.loads(selected_medication_data)
    return None

#Gets the Selected user from the pickle in the session
def get_selected_user():
    selected_user_data = session.get('selected_user')
    if selected_user_data:
        return pickle.loads(selected_user_data)
    return None

#Sets the selected user in a pickle and stores it in the session
def set_selected_user(user):
    session['selected_user'] = pickle.dumps(user)

#Sets the selected resident in a pickle and stores it in the session
def set_selected_resident(resident):
    session['selected_resident'] = pickle.dumps(resident)

#Sets the selected medication in a pickle and stores it in the session
def set_selected_medication(medication):
    session['selected_medication'] = pickle.dumps(medication)

#Verifies if the inputed id is in the designated lists
def verify_id(id, type):
    if type == 'User':
        user = db.get_caretaker(current_user.id)
        if user:
            set_selected_user(user)
        else:
            set_selected_user(db.get_nurse(current_user.id))
    elif type == 'Resident':
        for resident in get_selected_user().get_resident_list():
            if int(id) == resident.id:
                set_selected_resident(resident)
                break
    else:
        selected_resident = get_selected_resident()
        if selected_resident:
            for medication in selected_resident.get_medication_list():
                if int(id) == medication.id:
                    set_selected_medication(medication)
                    break


#Creates a route to the home page
@views.route('/',methods=['Get','Post'])
@login_required
def home():
    verify_id(0,"User")
    if request.method == 'POST':
        resident_id = request.form.get('resident_id')
        if resident_id:
            verify_id(resident_id,"Resident")
            return redirect(url_for('views.medication_list'))
    return render_template("home.html", resident_list=get_selected_user().get_resident_list())



#Creates a route to the medication list
@views.route('/medication-list',methods=['Get','Post'])
@login_required
def medication_list():
    selected_resident = get_selected_resident()
    if selected_resident:
        medication_list = selected_resident.get_medication_list()

        if request.method == 'POST':
            # Retrieve medication_id from the form data
            medication_id = request.form.get('medication_id')
            if medication_id:
                verify_id(medication_id,"Medication")
                return redirect(url_for('views.medication_dashboard'))



        return render_template('medication_list.html', resident=selected_resident, medication_list=medication_list)
    else:
        return "Resident not found", 404
    

#Creates a route to the medication dashboard
@views.route('/medication-dashboard',methods=['GET','POST'])
@login_required
def medication_dashboard():
    selected_resident = get_selected_resident()
    selected_medication = get_selected_medication()

    if selected_resident and selected_medication:
        # Create and serialize graphs
        graph1JSON = json.dumps(dash.createGraphOne(selected_medication, selected_resident), cls=plotly.utils.PlotlyJSONEncoder)
        graph2JSON = json.dumps(dash.createGraphTwo(selected_medication, selected_resident), cls=plotly.utils.PlotlyJSONEncoder)
        graph3JSON = json.dumps(dash.createGraphThree(selected_medication, selected_resident), cls=plotly.utils.PlotlyJSONEncoder)
        graph4JSON = json.dumps(dash.createGraphFour(selected_medication, selected_resident), cls=plotly.utils.PlotlyJSONEncoder)
        graph5JSON = json.dumps(dash.createGraphFive(selected_medication, selected_resident), cls=plotly.utils.PlotlyJSONEncoder)
        graph6JSON = json.dumps(dash.createGraphSix(selected_medication, selected_resident), cls=plotly.utils.PlotlyJSONEncoder)
        graph7JSON = json.dumps(dash.createGraphSeven(selected_medication, selected_resident), cls=plotly.utils.PlotlyJSONEncoder)
        graph8JSON = json.dumps(dash.createGraphEight(selected_medication, selected_resident), cls=plotly.utils.PlotlyJSONEncoder)

        return render_template("medication_dashboard.html", 
            graph1JSON=graph1JSON, graph2JSON=graph2JSON, graph3JSON=graph3JSON,
            graph4JSON=graph4JSON, graph5JSON=graph5JSON, graph6JSON=graph6JSON,
            graph7JSON=graph7JSON, graph8JSON=graph8JSON, 
            medication=selected_medication, resident=selected_resident)
    else:
        return "Resident or Medication not found", 404
