from flask import Blueprint,render_template
import json
import plotly
from . import dash
from website.config import db

#creates variable to hold all views in the file
views = Blueprint('views', __name__)
#Stores the list of all residents
resident_list = db.get_residents()

#Creates global variables to store the selected resident and medication
selected_resident = None
selected_medication = None

#Creates path to the home
@views.route('/')
def home():
    return render_template("home.html", resident_list=resident_list)

#Creates path to the medication list
@views.route('medication-list/<int:resident_id>')
def medication_list(resident_id):
    global selected_resident
    for resident in resident_list:
        if resident_id == resident.id:
            selected_resident = resident
            break

    if selected_resident:
        medication_list = db.get_medication_list(selected_resident)
        return render_template('medication_list.html', resident=selected_resident, medication_list= medication_list)
    else:
        return "Resident not found", 404

#Creates path to the medication dashboard
@views.route('/medication-dashboard/<int:medication_id>')
def medication_dashboard(medication_id):
        global selected_resident
        for medication in db.get_medication_list(selected_resident):
            if medication_id == medication.id:
                selected_medication = medication
                break
            
        # Graph One
        graph1JSON = json.dumps(dash.createGraphOne(selected_medication,selected_resident), cls=plotly.utils.PlotlyJSONEncoder)

        # Graph two
        graph2JSON = json.dumps(dash.createGraphTwo(selected_medication,selected_resident), cls=plotly.utils.PlotlyJSONEncoder)

        # Graph three
        graph3JSON = json.dumps(dash.createGraphThree(selected_medication,selected_resident), cls=plotly.utils.PlotlyJSONEncoder)

        # Graph four
        graph4JSON = json.dumps(dash.createGraphFour(selected_medication,selected_resident), cls=plotly.utils.PlotlyJSONEncoder)

        # Graph five
        graph5JSON = json.dumps(dash.createGraphFive(selected_medication,selected_resident), cls=plotly.utils.PlotlyJSONEncoder)

        # Graph six
        graph6JSON = json.dumps(dash.createGraphSix(selected_medication,selected_resident), cls=plotly.utils.PlotlyJSONEncoder)

        # Graph seven
        graph7JSON = json.dumps(dash.createGraphSeven(selected_medication,selected_resident), cls=plotly.utils.PlotlyJSONEncoder)

        # Graph eigth
        graph8JSON = json.dumps(dash.createGraphEight(selected_medication,selected_resident), cls=plotly.utils.PlotlyJSONEncoder)

        return render_template("medication_dashboard.html", graph1JSON = graph1JSON,  graph2JSON=graph2JSON, graph3JSON=graph3JSON,
                                                            graph4JSON = graph4JSON,  graph5JSON=graph5JSON, graph6JSON=graph6JSON,
                                                            graph7JSON = graph7JSON,  graph8JSON =graph8JSON, medication = selected_medication, resident = selected_resident)



