from flask import Blueprint, render_template, request, redirect, url_for, make_response
from flask_login import login_required
import json
import plotly
from . import dash
from .control import (
    get_selected_resident,
    verify_id,
    get_selected_user,
    get_selected_medication,
    create_med_list_pdf,
    med_administered,
    insert_new_medication,
    insert_wellness_check,
    get_medication_list_resident,
    get_vitals_list_resident,
    get_all_medication_names,
    create_new_caretaker,
    create_new_resident,
    get_resident_list,
    create_med_report_pdf,
)
from .models import Caretaker
import random

views = Blueprint("views", __name__)


# Creates a route to the home page
@views.route("/", methods=["GET", "POST"])
@login_required
def home():
    #Verifies the type of user logging in.
    verify_id(0, "User")
    #If a resident is clicked
    if request.method == "POST":
        #Store the resident id
        resident_id = request.form.get("resident_id")
        if resident_id:
            #Stores the clicked resident to the home page
            verify_id(resident_id, "Resident")
            #Move to the medication list page
            return redirect(url_for("views.medication_list"))
    #Else Get request, Show home page, validate what to show in the flyout menu and get the list of residents
    # associated with the user
    return render_template(
        "home.html",
        showMedicationList=False,
        add_resident = True,
        resident_list=get_resident_list(get_selected_user()),
    )

@views.route("/add-new-caretaker",methods=["GET"])
@login_required
def add_new_caretaker():
    return render_template("add_new_caretaker.html")


@views.route("/submit-new-caretaker",methods=["POST"])
@login_required
def submit_new_caretaker():
     # Get form data from the request
    email = request.form.get("email")
    first_name = request.form.get("first_name")
    initial = request.form.get("initial")
    paternal_last_name = request.form.get("paternal_last_name")
    maternal_last_name = request.form.get("maternal_last_name")
    phone_number = request.form.get("phone_number")

    if initial == '':
        initial = None
    if maternal_last_name == '':
        maternal_last_name = None

    create_new_caretaker(email,first_name,initial,paternal_last_name,maternal_last_name,phone_number)

    return redirect(url_for("views.add_new_resident"))


@views.route("/add-new-resident",methods=["GET"])
@login_required
def add_new_resident():
    return render_template("add_new_resident.html")


@views.route("/submit-new-resident",methods=["POST"])
@login_required
def submit_new_resident():
    # Get form data from the request
    first_name = request.form.get("first_name")
    initial = request.form.get("initial")
    paternal_last_name = request.form.get("paternal_last_name")
    maternal_last_name = request.form.get("maternal_last_name")
    image = request.form.get("image")
    birthday = request.form.get("birthday")
    height = request.form.get("height")
    submit_type = request.form.get('submit_value')

    if initial == '':
        initial = None
    if maternal_last_name == '':
        maternal_last_name = None

    if image == '':
        image = None

    create_new_resident(first_name,initial,paternal_last_name,maternal_last_name,image,birthday,height)

    if submit_type == '1':
        return redirect(url_for("views.add_new_resident"))
    else:
        return redirect(url_for("views.home"))



# Creates a route to the medication list
@views.route("/medication-list", methods=["GET", "POST"])
@login_required
def medication_list():
    selected_resident = get_selected_resident()
    if selected_resident:
        medication_list = get_medication_list_resident(get_selected_resident())
        print(medication_list)

        if request.method == "POST":
            medication_id = request.form.get("medication_id")
            if medication_id:
                verify_id(medication_id, "Medication")
                return redirect(url_for("views.medication_dashboard"))
        
        vitals_list = get_vitals_list_resident(get_selected_resident())

        temp_check = weight_check= systolic_bp_check = diastolic_bp_check = heart_rate_check = glucose_check = False

        min_temp = 97.5
        max_temp = 100.5

        resident_height = random.uniform(1.45, 1.95)

        min_BMI = 18.5
        max_BMI = 24.9

        min_systolic_bp = 91
        max_systolic_bp = 130

        min_diastolic_bp = 61
        max_diastolic_bp = 80

        min_heart_rate = 60
        max_heart_rate = 100

        min_glucose = 30
        max_glucose = 130

        resident_BMI = 0
        Emergency_Admin = []
        if len(vitals_list) >=1:
            latestVitals = vitals_list[-1]
           # resident_BMI = float(latestVitals.weight) / (resident_height ** 2)

            if latestVitals.temperature < min_temp or latestVitals.temperature > max_temp:
                temp_check = True

          #  if resident_BMI < min_BMI or resident_BMI > max_BMI:
           #     weight_check = True
            confirm,spike,outliers,range_t,baseline,all,match,dump = get_selected_resident().check_condition(get_medication_list_resident(get_selected_resident()),[vital.systolic_blood_pressure for vital in get_vitals_list_resident(get_selected_resident())])
            if confirm:
                Emergency_Admin = get_selected_resident().medication_condition(get_selected_resident().check_blood_pressure(),"BP" ,get_medication_list_resident(get_selected_resident()))
                print("Emergency Medication:", Emergency_Admin)

                systolic_bp_check = True

         #   if latestVitals.diastolic_blood_pressure < min_diastolic_bp or latestVitals.diastolic_blood_pressure > max_diastolic_bp:
               # diastolic_bp_check = True
            
            if latestVitals.heart_rate < min_heart_rate or latestVitals.heart_rate > max_heart_rate:
                heart_rate_check = True

            if latestVitals.glucose < min_glucose or latestVitals.glucose > max_glucose:
                glucose_check= True
        else:
            latestVitals = []

        for index in range(len(medication_list)):
            medication_list[index].calculate_priority(Emergency_Admin)

        # Custom sorting key function
        def sort_key(medication):
            return (medication.priority, medication.name)
        
        priority_medication = sorted(medication_list,key=sort_key)

        return render_template(
            "medication_list.html",
            showAddMedication=True if get_selected_user().role == "Nurse" else False,
            showMedicationList=True,
            add_resident = False,
            user=get_selected_user(),
            resident=selected_resident,
            medication_list=priority_medication,
            temp_check = temp_check,
            weight_check = weight_check,
            systolic_bp_check = systolic_bp_check,
            diastolic_bp_check = diastolic_bp_check,
            heart_rate_check = heart_rate_check,
            glucose_check = glucose_check,
            latestVitals = latestVitals,
            min_temp = 97.5,
            max_temp = 100.5,
            min_BMI = 18.5,
            max_BMI = 24.9,
            min_systolic_bp = 91,
            max_systolic_bp = 130,
            min_diastolic_bp = 61,
            max_diastolic_bp = 80,
            min_heart_rate = 60,
            max_heart_rate = 100,
            min_glucose = 30,
            max_glucose = 130,
            Emergency_Admin = Emergency_Admin,
        #    resident_BMI = round(resident_BMI,2),
        )
    else:
        return "Resident not found", 404


# Creates a route to the medication dashboard
@views.route("/add-medication-page", methods=["GET"])
@login_required
def add_medication_page():
    return render_template(
        "add_medication.html",
        known_medication=get_all_medication_names(),
        resident=get_selected_resident(),
    )


# Creates a route to the medication dashboard
@views.route("/add-medication", methods=["POST"])
@login_required
def add_medication():
    # Access form data using request.form
    medication_name = request.form.get("medicationName")
    route = request.form.get("route")
    dosage = request.form.get("dosage")
    pill_quantity = request.form.get("pillQuantity")
    pill_frequency = request.form.get("pillFrequency")
    refill_quantity = request.form.get("refillQuantity")
    start_date = request.form.get("startDate")
    prescription_date = request.form.get("prescriptionDate")
    description = request.form.get("description")

    insert_new_medication(medication_name,route,dosage,pill_quantity,pill_frequency,refill_quantity,start_date,prescription_date,description)

    
    return redirect(url_for("views.medication_list"))


# Creates a route to the medication dashboard
@views.route("/medication-dashboard", methods=["GET", "POST"])
@login_required
def medication_dashboard():
    #Get the selected Resident
    selected_resident = get_selected_resident()
    #Get the Selected Medication
    selected_medication = get_selected_medication()

    #If both have data then generate the medication dashboard
    if selected_resident and selected_medication:
        graph1JSON = json.dumps(dash.createGraphOne(selected_medication, selected_resident),cls=plotly.utils.PlotlyJSONEncoder,)
        graph2JSON = json.dumps(dash.createGraphTwo(selected_medication, selected_resident),cls=plotly.utils.PlotlyJSONEncoder,)
        graph3JSON = json.dumps(dash.createGraphThree(selected_medication, selected_resident),cls=plotly.utils.PlotlyJSONEncoder,)
        graph4JSON = json.dumps(dash.createGraphFour(selected_medication, selected_resident),cls=plotly.utils.PlotlyJSONEncoder,)
        graph5JSON = json.dumps(dash.createGraphFive(selected_medication, selected_resident),cls=plotly.utils.PlotlyJSONEncoder,)
        graph6JSON = json.dumps(dash.createGraphSix(selected_medication, selected_resident),cls=plotly.utils.PlotlyJSONEncoder,)
        graph7JSON = json.dumps(dash.createGraphSeven(selected_medication, selected_resident),cls=plotly.utils.PlotlyJSONEncoder,)
        graph8JSON = json.dumps(dash.createGraphEight(selected_medication, selected_resident),cls=plotly.utils.PlotlyJSONEncoder,)
        graph9JSON = json.dumps(dash.createGraphNine(selected_medication, selected_resident),cls=plotly.utils.PlotlyJSONEncoder,)
        graph10JSON = json.dumps(dash.createGraphTen(selected_medication, selected_resident),cls=plotly.utils.PlotlyJSONEncoder,)
        
        return render_template("medication_dashboard.html",
            graph1JSON=graph1JSON,graph2JSON=graph2JSON,graph3JSON=graph3JSON,
            graph4JSON=graph4JSON,graph5JSON=graph5JSON,graph6JSON=graph6JSON,
            graph7JSON=graph7JSON,graph8JSON=graph8JSON,graph9JSON=graph9JSON,
            graph10JSON=graph10JSON,medication=selected_medication,resident=selected_resident,
            showMedicationList=False,
        )
    else:
        return "Resident or Medication not found", 404


@views.route("/generate-medication-list")
@login_required
def generate_pdf():
    # Create a PDF document using reportlab
    resident = get_selected_resident()
    response = make_response(create_med_list_pdf(resident))
    response.headers["Content-Type"] = "application/pdf"
    response.headers[
        "Content-Disposition"
    ] = "inline; filename={0} Medication List.pdf".format(
        get_selected_resident().get_full_name()
    )
    return response

@views.route("/generate-medication-report")
@login_required
def generate_report_pdf():
    # Create a PDF document using reportlab
    resident = get_selected_resident()
    response = make_response(create_med_report_pdf(resident))
    response.headers["Content-Type"] = "application/pdf"
    response.headers[
        "Content-Disposition"
    ] = "inline; filename={0} Medication Report.pdf".format(
        get_selected_resident().get_full_name()
    )
    return response

@views.route("/administer-medication", methods=["POST"])
@login_required
def administer():
    medication_id = request.form.get("medication_id")
    med_administered(medication_id)
    return "Medication Administered Successfully"



@views.route("/perform-wellness-check", methods=["GET"])
@login_required
def perform_wellness_check():
    return render_template("wellness_check.html", resident = get_selected_resident())


@views.route("/submit-wellness-check", methods=["POST"])
@login_required
def submit_wellness_check():
    feeling = request.form.get('feeling')
    description = request.form.get('description')
    temperature = request.form.get('temperature')
    weight = request.form.get('weight')
    systolic_bp = request.form.get('systolic_bp')
    diastolic_bp = request.form.get('diastolic_bp')
    heart_rate = request.form.get('heart_rate')
    glucose = request.form.get('glucose')

    insert_wellness_check(feeling,description,temperature, weight, systolic_bp,diastolic_bp,heart_rate,glucose)

    return redirect(url_for("views.medication_list"))