from flask import Blueprint, render_template, request, redirect, url_for, make_response
from flask_login import login_required
import json
import plotly
from . import dash
from .control import (get_selected_resident,verify_id,get_selected_user,
                      get_selected_medication,create_med_list_pdf,med_administered,
                      insert_new_medication, insert_wellness_check,get_medication_list_resident,
                      get_all_medication_names,create_new_caretaker,create_new_resident,
                      get_resident_list,create_med_report_pdf,delete_img_graphs,
                      create_qr_codes,add_refill_medication,get_all_diagnosis_names,)

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
    return render_template("home.html",showMedicationList=False,add_resident = True,
        resident_list=get_resident_list(get_selected_user()),show_qr_code = True
    )

#Route to add new caretaker
@views.route("/add-new-caretaker",methods=["GET"])
@login_required
def add_new_caretaker():
    return render_template("add_new_caretaker.html")

#Route to submit a new caretaker
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


#Route to add a new resident
@views.route("/add-new-resident",methods=["GET"])
@login_required
def add_new_resident():
    return render_template("add_new_resident.html")

#Route to submit a new resident
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

#Route to the medication list
@views.route("/medication-list", methods=["GET", "POST"])
@login_required
def medication_list():
    validate = False
    selected_resident = get_selected_resident()

    if selected_resident:
        for resident in get_resident_list(get_selected_user()):
            if resident.id == selected_resident.id:
                validate = True

    if validate:
        if selected_resident:
            medication_list = get_medication_list_resident(get_selected_resident())
            delete_img_graphs()

            if request.method == "POST":
                medication_id = request.form.get("medication_id")
                if medication_id:
                    verify_id(medication_id, "Medication")
                    return redirect(url_for("views.medication_dashboard"))
                
            #Default all conditions to False
            temp_check = weight_check= systolic_bp_check = diastolic_bp_check = heart_rate_check = glucose_check = False

            Emergency_Admin = []

            active_flags = selected_resident.get_active_flags()

            # resident_BMI = float(latestVitals.weight) / (resident_height ** 2)

            if "Temp" in active_flags:
                Emergency_Admin += get_selected_resident().medication_condition("Temperature", get_medication_list_resident(get_selected_resident()))
                temp_check = True

            #  if resident_BMI < min_BMI or resident_BMI > max_BMI:
            #     weight_check = True

            # confirm,spike,outliers,range_t,baseline,all,match,dump = get_selected_resident().check_condition(get_medication_list_resident(get_selected_resident()),[vital.systolic_blood_pressure for vital in get_vitals_list_resident(get_selected_resident())])
            # if confirm:
            if any(category in active_flags for category in ["Low Blood Pressure", "Pre-Hypertension", "High: Stage 1 Hypertension", "High: Stage 2 Hypertension"]):
                Emergency_Admin += get_selected_resident().medication_condition("Blood Pressure", get_medication_list_resident(get_selected_resident()))
                systolic_bp_check = True

            if "Heart Rate" in active_flags:
                Emergency_Admin += get_selected_resident().medication_condition("Pulse", get_medication_list_resident(get_selected_resident()))
                heart_rate_check = True

            if "Glucose" in active_flags:
                Emergency_Admin += get_selected_resident().medication_condition("Glucose", get_medication_list_resident(get_selected_resident()))
                glucose_check= True

            for index in range(len(medication_list)):
                medication_list[index].calculate_priority(Emergency_Admin)

            # Custom sorting key function
            def sort_key(medication):
                return (medication.priority, medication.name)
            
            priority_medication = sorted(medication_list,key=sort_key)

            return render_template("medication_list.html",showAddMedication=True if get_selected_user().role == "Nurse" else False,
                showMedicationList= True,
                nurse_duty = True if get_selected_user().role == "Nurse" else False,
                show_qr_code = False,
                add_resident = False,user=get_selected_user(),resident=selected_resident,
                medication_list=priority_medication,temp_check = temp_check,weight_check = weight_check,
                systolic_bp_check = systolic_bp_check,diastolic_bp_check = diastolic_bp_check,
                heart_rate_check = heart_rate_check,glucose_check = glucose_check,
                Emergency_Admin = Emergency_Admin,
            )
        else:
            return render_template("404_page.html")
    else:
        return render_template("404_page.html")

#Route to the qr code
@views.route("/qr-medication/<int:resident_id>")
@login_required
def redirect_resident(resident_id):
    verify_id(resident_id, "Resident")
    return redirect(url_for("views.medication_list"))

# Creates a route to the medication dashboard
@views.route("/add-medication-page", methods=["GET"])
@login_required
def add_medication_page():
    return render_template(
        "add_medication.html",
        known_medication=get_all_medication_names(),
        known_diagnosis = get_all_diagnosis_names(),
        resident=get_selected_resident(),
    )

# Creates a route to the medication dashboard
@views.route("/refill-medication", methods=["POST"])
@login_required
def add_refill():
    medication_id = request.form.get("medication_id")
    add_refill_medication(medication_id)
    return "Medication Refilled Successfully"


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
    selected_purposes = request.form.getlist('medicationPurpose[]')

    insert_new_medication(medication_name,route,dosage,pill_quantity,pill_frequency,refill_quantity,start_date,prescription_date,selected_purposes)

    
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

#Route to the medication list
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

#Route for the comprehensive medical report
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

#Route to admisnter medication
@views.route("/administer-medication", methods=["POST"])
@login_required
def administer():
    medication_id = request.form.get("medication_id")
    med_administered(medication_id)
    return "Medication Administered Successfully"


#Route to preform a wellness check
@views.route("/perform-wellness-check", methods=["GET"])
@login_required
def perform_wellness_check():
    return render_template("wellness_check.html", resident = get_selected_resident())

#Route to submit the wellness check
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

#Route to generate the QR CODE
@views.route("/generate-qr-codes")
@login_required
def generate_all_qr_codes():
    # Create a PDF document using reportlab
    resident_list = get_resident_list(get_selected_user())
    response = make_response(create_qr_codes(resident_list))
    response.headers["Content-Type"] = "application/pdf"
    response.headers[
        "Content-Disposition"
    ] = "inline; filename=Residents QR CODES.pdf"
    return response

#Route to the qr code
@views.route("/generate-qr-code")
@login_required
def generate_qr_code():
    # Create a PDF document using reportlab
    resident = get_selected_resident()
    response = make_response(create_qr_codes([resident]))
    response.headers["Content-Type"] = "application/pdf"
    response.headers[
        "Content-Disposition"
    ] = f"inline; filename={resident.get_full_name()} QR CODE.pdf"
    return response