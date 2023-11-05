from flask import Blueprint, render_template, request, redirect, url_for,make_response
from flask_login import login_required
import json
import plotly
from . import dash
from .control import get_selected_resident, verify_id, get_selected_user,get_selected_medication, create_med_list_pdf,med_administered

views = Blueprint('views', __name__)

#Creates a route to the home page
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    verify_id(0, "User")
    #TODO: When Nurse page is created add an if statement that checks if the role is caretaker or nurse and display the correct page
    if request.method == 'POST':
        resident_id = request.form.get('resident_id')
        if resident_id:
            verify_id(resident_id, "Resident")
            return redirect(url_for('views.medication_list'))
    return render_template("home.html",showMedicationList = False ,resident_list=get_selected_user().get_resident_list())

#Creates a route to the medication list
@views.route('/medication-list', methods=['GET', 'POST'])
@login_required
def medication_list():
    selected_resident = get_selected_resident()
    if selected_resident:
        medication_list = selected_resident.get_medication_list()

        if request.method == 'POST':
            medication_id = request.form.get('medication_id')
            if medication_id:
                verify_id(medication_id, "Medication")
                return redirect(url_for('views.medication_dashboard'))

        return render_template('medication_list.html',showMedicationList = True ,user=get_selected_user() ,resident=selected_resident, medication_list=medication_list)
    else:
        return "Resident not found", 404
    
#Creates a route to the medication dashboard
@views.route('/medication-dashboard', methods=['GET', 'POST'])
@login_required
def medication_dashboard():
    selected_resident = get_selected_resident()
    selected_medication = get_selected_medication()

    if selected_resident and selected_medication:
        graph1JSON = json.dumps(dash.createGraphOne(selected_medication, selected_resident), cls=plotly.utils.PlotlyJSONEncoder)
        graph2JSON = json.dumps(dash.createGraphTwo(selected_medication, selected_resident), cls=plotly.utils.PlotlyJSONEncoder)
        graph3JSON = json.dumps(dash.createGraphThree(selected_medication, selected_resident), cls=plotly.utils.PlotlyJSONEncoder)
        graph4JSON = json.dumps(dash.createGraphFour(selected_medication, selected_resident), cls=plotly.utils.PlotlyJSONEncoder)
        graph5JSON = json.dumps(dash.createGraphFive(selected_medication, selected_resident), cls=plotly.utils.PlotlyJSONEncoder)
        graph6JSON = json.dumps(dash.createGraphSix(selected_medication, selected_resident), cls=plotly.utils.PlotlyJSONEncoder)
        graph7JSON = json.dumps(dash.createGraphSeven(selected_medication, selected_resident), cls=plotly.utils.PlotlyJSONEncoder)
        graph8JSON = json.dumps(dash.createGraphEight(selected_medication, selected_resident), cls=plotly.utils.PlotlyJSONEncoder)
        graph9JSON = json.dumps(dash.createGraphNine(selected_medication, selected_resident), cls=plotly.utils.PlotlyJSONEncoder)
        graph10JSON = json.dumps(dash.createGraphTen(selected_medication, selected_resident), cls=plotly.utils.PlotlyJSONEncoder)

        return render_template("medication_dashboard.html", 
            graph1JSON=graph1JSON, graph2JSON=graph2JSON, graph3JSON=graph3JSON,
            graph4JSON=graph4JSON, graph5JSON=graph5JSON, graph6JSON=graph6JSON,
            graph7JSON=graph7JSON, graph8JSON=graph8JSON, graph9JSON=graph9JSON,
            graph10JSON=graph10JSON, medication=selected_medication, resident=selected_resident,showMedicationList = False)
    else:
        return "Resident or Medication not found", 404
    

@views.route('/generate-medication-list')
def generate_pdf():
    # Create a PDF document using reportlab
    resident = get_selected_resident()
    response = make_response(create_med_list_pdf(resident))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename={0} Medication List.pdf'.format(get_selected_resident().get_full_name())
    return response


@views.route('/administer-medication',methods=['POST'])
def administer():
    medication_id = request.form.get('medication_id')
    med_administered(medication_id)
    return "Medication Administered Successfully"