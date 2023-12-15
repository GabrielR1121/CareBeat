from flask import session
import pickle
from website.config import db
from .models import Wellness_check,Vitals
from flask_login import current_user
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle, Paragraph, PageTemplate,Frame,Image ,BaseDocTemplate,Spacer,PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from reportlab.pdfgen import canvas
import datetime
import secrets
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .models import Caretaker
from datetime import datetime
import qrcode
from website.config import config
'''
File that has all the control code. 
All the code that is run in the views.py is created here.
'''

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


#Gets the Selected user from the pickle in the session
def get_selected_caretaker():
    selected_user_data = session.get('selected_caretaker')
    if selected_user_data:
        return pickle.loads(selected_user_data)
    return None

#Sets the selected user in a pickle and stores it in the session
def set_selected_caretaker(user):
    session['selected_caretaker'] = pickle.dumps(user)


#Sets the selected resident in a pickle and stores it in the session
def set_selected_resident(resident):
    session['selected_resident'] = pickle.dumps(resident)

#Sets the selected medication in a pickle and stores it in the session
def set_selected_medication(medication):
    session['selected_medication'] = pickle.dumps(medication)

#Verifies if the inputed id is in the designated lists
def verify_id(id, type):
    #Validates if the user logging in is a Caretaker or Nurse
    if type == 'User':
        user = db.get_caretaker(current_user.id)
        #If the User is a caretaker
        if user:
            #Store the caretaker to the Flask Session
            set_selected_user(user)
        else:
            #Store the nurse to the flask session
            set_selected_user(db.get_nurse(current_user.id))
    elif type == 'Resident':
        #When a resident is selected in the Home Page find the resident Object
        # and store it to the flask session
        for resident in get_selected_user().get_resident_list():
            if int(id) == resident.id:
                set_selected_resident(resident)
                break
    else:
        # When a medication for a resident is selected store the selected medication
        # to the flask session
        selected_resident = get_selected_resident()
        if selected_resident:
            for medication in db.get_medication_list(selected_resident):
                if int(id) == medication.id:
                    set_selected_medication(medication)
                    break

# Execution code for when a medication is administered
# Receives the id of the clicked medication
# Returns a message if all worked correctly
def med_administered(med_id):
    for medication in get_medication_list_resident(get_selected_resident()):
        if int(med_id) == medication.id:
            db.insert_into_pill(medication,get_selected_resident(),get_selected_user())
            print("medication was administered")
            break
# Execution code for when a medication is refilled
# Receives the id of the clicked medication
# Returns a message if all worked correctly
def add_refill_medication(med_id):
    for medication in get_medication_list_resident(get_selected_resident()):
        if int(med_id) == medication.id:
            db.insert_into_refill(medication,get_selected_resident())
            medication.refill_bool = True
            print("medication was refilled")
            break


# Get the list of residents associated with the logged in user
# Receives the user object
# Returns the list of residents
def get_resident_list(user):
    return db.get_residents(user)

# Inserts a new medication 
# Receives all the medication attributes for insertion
def insert_new_medication(medication_name,route,dosage,pill_quantity,pill_frequency,refill_quantity,start_date,prescription_date,diagnosis_list):
    id = db.find_med_id(medication_name)
    db.add_new_medication(get_selected_resident(),id,medication_name,route,dosage,pill_quantity,pill_frequency,refill_quantity,start_date,prescription_date,diagnosis_list)

# Insert welness check and vitals
# recieves all the atributes from wellness check and vitals
def insert_wellness_check(feeling, description, temperature,weight,systolic_bp,diastolic_bp,heart_rate,glucose):
    vitals = None
    if any([temperature, weight,systolic_bp, diastolic_bp, heart_rate, glucose]):
        vitals = Vitals(temperature= temperature, weight = weight,systolic_blood_pressure=systolic_bp,diastolic_blood_pressure=diastolic_bp,heart_rate=heart_rate,glucose=glucose)

    wellness = Wellness_check( rating = feeling, description= description)
    db.insert_wellness_check(wellness,get_selected_resident(),vitals)

#Gets the medication list linked to a specific resident
# Returns a list of medication objects
def get_medication_list_resident(resident):
    return db.get_medication_list(resident)

#Gets the vitals list liked with a resident
# Returns a list of vitals objects 
def get_vitals_list_resident(resident):
    return db.get_vitals(resident)

#Gets the wellness check list linked with a resident
# Returns a list of wellness check objects
def get_wellness_check_list_resident(resident):
    return db.get_wellness_checks(resident)

#Gets the refill list linked with a resident
# Returns a list of refill objects 
def get_refill_list_resident(resident,medication):
    return db.get_refill_list(resident,medication)

#Gets the caretaker linked to a resident 
# Returns a caretaker object 
def get_caretaker_resident(resident):
    return db.get_caretaker_resident(resident)


#Gets a list of strings with the medication names
# Returns a list of strings with all the medication names
def get_all_medication_names():
    return db.get_all_medication_names()

#Gets a list of strings with the diagnosis names
# Returns a list of strings with all the diagnosis names
def get_all_diagnosis_names():
    return db.get_all_diagnosis_names()

#Generates a temp password for caretakers
# Returns a secure password
def generate_password(length=12):
    # Define characters to include in the password
    characters = string.ascii_letters + string.digits + string.punctuation
    
    # Use secrets module to generate a secure random password
    password = ''.join(secrets.choice(characters) for _ in range(length))
    
    return password

#Inserts a new Caretaker
def create_new_caretaker(email, first_name,initial, paternal_last_name, maternal_last_name, phone_number):

    password = generate_password(10)
    id = db.create_new_caretaker(email, password ,first_name,initial, paternal_last_name, maternal_last_name, phone_number)

    set_selected_caretaker(Caretaker("Caretaker", id,first_name,email,password,initial,paternal_last_name,maternal_last_name,phone_number,"T-Mobil",5000))
    pass

#Inserts a new Resident
def create_new_resident(first_name,initial,paternal_last_name,maternal_last_name,image,birthday,height):
    db.create_new_resident(first_name,initial,paternal_last_name,maternal_last_name,image,birthday,height,get_selected_caretaker().id,get_selected_caretaker().nursing_home_id)

#Creates the medicaiton list pdf 
# Returns a Buffer object with all the pdf information 
def create_med_list_pdf(resident):
    # Create a buffer to store the PDF data
    buffer = BytesIO()

    # Create a PDF document
    doc = BaseDocTemplate(buffer, pagesize=letter, topMargin=0, leftMargin=0, rightMargin=0, bottomMargin=0)

    styles = getSampleStyleSheet()

    # Create the story (content) of the document
    story = []

    title = Paragraph("All Medications", styles['Title'])

    # Define data dynamically using a for loop
    data = [[title,'','','','',''],
            ['Medication Name', 'Dosage (mg)','I take this for' ,'Morning\n(6 am - 10am)', 'Noon\n(11 am - 1 pm)', 'Evening\n(2 pm - 7 pm)', 'Bedtime\n(8 pm - 5 am)']]

    # Loops through the medication list and adds them to the medication list
    for medication in db.get_medication_list(resident):
        test = []  # Create a new list for each medication
        for diagnostic in set(diagnosis.name for diagnosis in medication.get_diagnosis_list()):
            test.append(diagnostic + " ")
        data.append([medication.name, medication.dosage, ', \n'.join(test), medication.morning_bool, medication.noon_bool, medication.evening_bool, medication.bedtime_bool])

    table = Table(data)  # Auto-adjust column widths based on content

   

    table.setStyle(TableStyle([
    ('SPAN', (0, 0), (-1, 0)),
    ('BACKGROUND', (0, 0), (-1, 0), (0.5372549019607843, 0.8117647058823529, 0.9411764705882353)),
    ('BACKGROUND', (0, 1), (-1, 1), (1.0, 0.733, 0.471)),
    ('TEXTCOLOR', (0, 0), (-1, 0), (0, 0, 0)),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 2), (-1, -1), (1,1,1)),
    ('GRID', (0, 0), (-1, -1), 1, (0, 0, 0)),
    ('GRID', (0, 1), (-1, -1), 1, (0, 0, 0)),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Center content vertically in all cells
    ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),  # Set the font size for the entire table
    ]))

    story.append(table)

    # Create a Spacer to separate the table from the footer note
    footer_note = Paragraph("<font color='#888888'>Displays medication intake analysis, not the prescribed one.</font>", styles['Normal'])

    story.append(footer_note)

    # Create a PageTemplate for the custom header
    header_frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height - 100, id='header')
    header_template = PageTemplate(id='Page', frames=[header_frame], onPage=lambda canvas, doc: header(canvas, doc, resident.get_full_name(),"List"))
    doc.addPageTemplates([header_template])

    # Build the PDF document
    doc.build(story)

    # Reset the buffer position to the beginning
    buffer.seek(0)

    # Return the buffer containing the PDF data
    return buffer

# Function to determine the background color based on blood pressure values
def get_background_color_bp(systolic, diastolic):
        if 70 <= systolic <= 90 and 40 <= diastolic <= 60:
            return '#458CCC'
        elif 90 <= systolic <= 121 or 60 <= diastolic <= 81:
            return '#77BB66'
        elif 121 <= systolic <= 140 or 81 <= diastolic <= 90:
            return '#F7A64A'
        elif 140 <= systolic <= 160 or 90 <= diastolic <= 100:
            return '#F07C7F'
        elif systolic > 160 or diastolic > 100:
            return '#F1444A'
        
# Function to determine the background color based on blood pressure values
def get_background_color_glucose(glucose):
    if 94 <= glucose <= 140:
        return '#77BB66'
    elif 140 <= glucose <= 160:
        return '#F7A64A'
    else:
        return '#F1444A'
    
# Function to determine the background color based on blood pressure values
def get_background_color_pulse(pulse):
    if pulse <= 59:
        return '#458CCC'
    elif 60 <= pulse < 100:
        return '#77BB66'
    elif 100 <= pulse < 120:
        return '#F7A64A'
    elif 120 <= pulse < 150:
        return '#F7A64A'
    else:
        return '#F1444A'
    
# Function to determine the background color based on blood pressure values
def get_background_color_temp(temp):
    if temp <95:
        return '#458CCC'
    elif 95 <= temp < 100.4:
        return '#77BB66'
    elif 100.4 <= temp < 104.0:
        return '#F7A64A'
    else:
        return '#F1444A'
    
def get_background_color_medication():
        return "#FBF719"
       
def delete_img_graphs():
    import os
    '''
    Method to delete created graphs in the medication report in order to safe space
    '''
    #Image graph names to make it easier for deletion
    images_to_delete = ['glucose_image.png', 'bp_image.png','pulse_image.png','temp_image.png']
    directory_path = r'website\static\images'

    #Deletes the designated files
    try:
        for filename in os.listdir(directory_path):
            if filename in images_to_delete:
                file_path = os.path.join(directory_path, filename)
                os.remove(file_path)
                print(f'{file_path} has been deleted successfully.')
    except OSError as e:
            if 'No such file or directory' in str(e):
                print(f'Error: Files in {directory_path} have already been deleted.')
            else:
                print(f'Error deleting files in {directory_path}: {e}')

#Creates a comprehensive medical report with all information the resident information
# Returns the buffer with all the pdf information
def create_med_report_pdf(resident):
   # Create a buffer to store the PDF data
    buffer = BytesIO()

    # Create a PDF document
    doc = BaseDocTemplate(buffer, pagesize=letter, topMargin=0, leftMargin=0, rightMargin=0, bottomMargin=0)

    styles = getSampleStyleSheet()

    styles['Normal'].fontSize = 12  # Change 12 to the desired font size
    styles['Title'].fontSize = 16  # Change 16 to the desired font size

    # Create the story (content) of the document
    story = []

    # Add the image
    image_path = resident.get_image().replace("..","website")
    image = Image(image_path, width=100, height=100)  # Adjust the width and height as needed

    caretaker_info = get_caretaker_resident(get_selected_resident())

    # Create a table with one row and four columns
    data = [
        [image,
        Paragraph(f"<b>Full Name:</b><br/> {resident.get_full_name()}", styles['Normal']),
        Paragraph(f"<b>Age:</b> <br/>{resident.get_age()}", styles['Normal']),
        Paragraph(f"<b>Date of Birth:</b><br/> {resident.birthday}\n", styles['Normal']),
        ],
        [ None,
        Paragraph(f"<b>Caretaker Name:</b><br/> {caretaker_info.get_full_name()}", styles['Normal']),
        Paragraph(f"<b>Email:</b> <br/>{caretaker_info.email}", styles['Normal']),
        Paragraph(f"<b>Phone #:</b> <br/>{caretaker_info.phone_number}", styles['Normal'])
        ]
    ]

    # Calculate the maximum width for each column
    #col_widths = [max(Paragraph(cell, styles['Normal']).wrap(100, 100)[0] for cell in col) for col in zip(*data)]

    table = Table(data,rowHeights=50)

    # Style the table to align the image to the left and text with the upper border of the image
    table.setStyle(TableStyle([
    ('ALIGN', (0, 0), (0, 0), 'LEFT'),
    ('VALIGN', (0, 0), (0, 0), 'TOP'),
    ('VALIGN', (1, 0), (-1, -1), 'TOP'),
    ]))

    # Build the PDF document
    story.append(table)


    # Add a Spacer (optional) to create some space between the table and the rectangle
    story.append(Spacer(1, 50))  # Adjust the space as needed\

    title = Paragraph("All Medications", styles['Title'])
    # Define data dynamically using a for loop
    data = [[title,'','','','',''],
            ['Medication Name', 'Dosage (mg)','I take this for' ,'Morning\n(6 am - 10am)', 'Noon\n(11 am - 1 pm)', 'Evening\n(2 pm - 7 pm)', 'Bedtime\n(8 pm - 5 am)']]
    highlight = []
    for medication in db.get_medication_list(resident):
        test = []  # Create a new list for each medication
        for diagnostic in set(diagnosis.name for diagnosis in medication.get_diagnosis_list()):
            test.append(diagnostic + " ")
        data.append([medication.name, medication.dosage, ', \n'.join(test), medication.morning_bool, medication.noon_bool, medication.evening_bool, medication.bedtime_bool])
        current_date = datetime.now()
        if (medication.start_date.year == current_date.year and medication.start_date.month == current_date.month):
            highlight.append(medication.name)
    table = Table(data)  # Auto-adjust column widths based on content

   

    table.setStyle(TableStyle([
    ('SPAN', (0, 0), (-1, 0)),
    ('BACKGROUND', (0, 0), (-1, 0), (0.5372549019607843, 0.8117647058823529, 0.9411764705882353)),
    ('BACKGROUND', (0, 1), (-1, 1), (1.0, 0.733, 0.471)),
    ('TEXTCOLOR', (0, 0), (-1, 0), (0, 0, 0)),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 2), (-1, -1), (1,1,1)),
    ('GRID', (0, 0), (-1, -1), 1, (0, 0, 0)),
    ('GRID', (0, 1), (-1, -1), 1, (0, 0, 0)),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Center content vertically in all cells
    ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),  # Set the font size for the entire table
    ]))

    # Modify the background color based on medication values
    for i, row in enumerate(data[2:]):
        background_color = None
        if row[0] in highlight:
            background_color = get_background_color_medication()
        if background_color:
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, i + 2), (-1, i + 2), background_color),
            ]))

    story.append(table)

    # Create a Spacer to separate the table from the footer note
    footer_note = Paragraph("<font color='#888888'>Displays medication intake analysis, not the prescribed one.</font>", styles['Normal'])


     # Create a new table for the legend
    legend_data = [
        ["Legend"],
        [f"Medication Started in {datetime.now().strftime('%B')}"],
    ]

    legend_table0 = Table(legend_data)
    # Set the style for the legend table to show grid lines
    legend_table0.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Add grid lines for all cells
        ('SPAN', (0, 0), (-1, 0)),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Make the first row bold
        ('BACKGROUND', (0, 0), (-1, 0), "#CCCCCC"),  # Set background color of the second row to "#CCCCCC"
        ('BACKGROUND', (0, 1), (0, 1), "#FBF719"),  # Change background color of the first cell in the second row

    ]))
    story.append(footer_note)
    story.append(Spacer(1,20))
    story.append(legend_table0)
    # Add a page break to start a new page
    story.append(PageBreak())

    # Create a PageTemplate for the custom header and section
    header_frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height - 100, id='header')
    header_template = PageTemplate(id='header', frames=[header_frame], onPage=lambda canvas, doc: header(canvas, doc, resident.get_full_name(), "Report"))
    doc.addPageTemplates([header_template])

     # Create a new table for blood pressure data
    bp_data = [
        ["Blood Pressure Readings"],
        ["Date/Time", "Systolic (mmHg)", "Diastolic (mmHg)"], # Leave placeholders for the latest readings
    ]

    # Assuming get_vitals_list_resident returns a list of vital readings
    vitals_list = get_vitals_list_resident(get_selected_resident())
    # Get the latest 6 readings based on timestamp
    latest_readings = sorted(vitals_list, key=lambda x: x.timestamp, reverse=True)[:5]

    for vital in latest_readings:
        bp_data.append([vital.timestamp, vital.systolic_blood_pressure, vital.diastolic_blood_pressure])

    bp_data.append( ["Baseline", f"{resident.get_baseline([systolic.systolic_blood_pressure for systolic in get_vitals_list_resident(get_selected_resident())])}", f"{resident.get_baseline([diastolic.diastolic_blood_pressure for diastolic in resident.get_vitals_list()])}"])

    bp_table = Table(bp_data, colWidths=[120, 100, 100])
    

    # Style the blood pressure table
    bp_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (-1, 0)),  # Span the first row across all columns
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertically center the text
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Make the first row bold
        ('FONTSIZE', (0, 0), (-1, 0), 14),  # Increase the font size for the first row
        ('FONTSIZE', (0, 1), (-1, 1), 12),  # Increase the font size for the first row
        ('FONTSIZE', (0, 2), (-1, -1), 11),  # Adjust the font size as needed
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),  # Add some padding to the bottom of cells
        ('BACKGROUND', (0, 0), (-1, 0), "#003366"),  # Set background color of the first row to "#003366"
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Set text color of the first row to white
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Add grid lines for all cells
        ('GRID', (0, -1), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, 1), "#CCCCCC"),  # Set background color of the second row to "#CCCCCC"
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.black),  # Set text color of the second row to black
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),  # Make the second row bold
         # Make the bottom row bold
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        # Increase the thickness of border lines for the bottom row
        ('GRID', (0, -1), (-1, -1), 3, colors.black),
    ]))

        # Modify the background color based on blood pressure values
    for i, row in enumerate(bp_data[2:]):
        systolic_value = float(row[1])
        diastolic_value = float(row[2])
        background_color = get_background_color_bp(systolic_value, diastolic_value)
        if background_color:
            bp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, i + 2), (-1, i + 2), background_color),
            ]))

    # Create a new table for the legend
    legend_data = [
        ["Legend","","","",""],
        ["Low","Normal","Pre-Hypertension","Hypertension Stage 1","Hypertension Stage 2"],
    ]

    legend_table = Table(legend_data)
    # Set the style for the legend table to show grid lines
    legend_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Add grid lines for all cells
        ('SPAN', (0, 0), (-1, 0)),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Make the first row bold
        ('BACKGROUND', (0, 0), (-1, 0), "#CCCCCC"),  # Set background color of the second row to "#CCCCCC"
        ('BACKGROUND', (0, 1), (0, 1), "#458CCC"),  # Change background color of the first cell in the second row
        ('BACKGROUND', (1, 1), (1, 1), "#77BB66"),  # Change background color of the second cell in the second row
        ('BACKGROUND', (2, 1), (2, 1), "#F7A64A"),  # Change background color of the third cell in the second row
        ('BACKGROUND', (3, 1), (3, 1), "#F07C7F"),  # Change background color of the fourth cell in the second row
        ('BACKGROUND', (4, 1), (4, 1), "#F1444A"),  # Change background color of the fifth cell in the second row

    ]))
    
    # Create a new centered style with adjusted margins and increased line spacing
    centered_style = ParagraphStyle(
        'centered',
        parent=styles['Normal'],
        alignment=0,  # 0=left, 1=center, 2=right
        leftIndent=20,  # Adjust the left margin
        rightIndent=20,  # Adjust the right margin
        spaceBefore=12,  # Double spacing: Adjust the space before each paragraph
    )

    graph_data = resident.check_condition(db.get_medication_list(get_selected_resident()),[vital.systolic_blood_pressure for vital in get_vitals_list_resident(get_selected_resident())])

    import plotly.graph_objects as go
    import plotly.io as pio

    # Check if graph_data is an integer
    if isinstance(graph_data, int):
        # Create an empty graph with tables
        fig = go.Figure()

        # Add title
        fig.update_layout(title='No Data Available')

    else:
        # Create figure with secondary y-axis
        fig = go.Figure()

        # Plot baseline and systolic BP on the first y-axis
        fig.add_trace(go.Scatter(x=list(graph_data[3]), y=graph_data[4], mode='lines', name='Baseline', line=dict(color='red', dash='dash')))
        fig.add_trace(go.Scatter(x=list(graph_data[3]), y=graph_data[7], mode='lines+markers', name='Blood Pressure', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=graph_data[5], y=graph_data[1], mode='lines+markers', name='Exceedance Alert', line=dict(color='orange', dash='dash'), marker=dict(color='orange')))

        # Plot medication start dates as vertical lines
        for i, medication in enumerate(graph_data[6]):
            fig.add_shape(go.layout.Shape(type="line", x0=i, x1=i, y0=0, y1=1, line=dict(color='gray', dash='dash'), xref="x", yref="paper"))
            fig.add_trace(go.Scatter(x=[0], y=[120], mode='markers', marker=dict(color='gray'), name=f'Medication Start: {medication.name}'))

        # Add first y-axis labels
        fig.update_layout(
            xaxis=dict(title='Time'),
            yaxis=dict(title='Blood Pressure Levels', side='left', color='blue'),
            legend=dict(x=1.1, y=0.3, traceorder='normal', orientation='h'),
        )

        # Retrieve wellness data for the selected resident
        current_wellness = [wellness for wellness in get_wellness_check_list_resident(resident)]

        # Create a twin Axes for the second y-axis
        fig.add_trace(go.Scatter(x=list(range(len(current_wellness))), y=[wellness.rating for wellness in current_wellness], mode='lines+markers', name='Wellness Check', line=dict(color='green'), yaxis='y2'))

        fig.update_layout(
            yaxis2=dict(title='Wellness Check', overlaying='y', side='right', color='green'),
        )

        # Add title and grid
        fig.update_layout(
            title='Blood Pressure and Wellness Check Correlation',
            title_x=0.2,
            showlegend=True,
        )

    # Save the image
    graph_image_path = r"website\static\images\bp_image.png"  # Replace with the actual path where you want to save the image
    pio.write_image(fig, graph_image_path)

    # Add content for the second page (you can customize this according to your needs)
    second_page_content = [
        bp_table,
        Spacer(1, 20),
        legend_table,
        Spacer(1, 10),
    ]
    analytics_paragraphs = get_analytics_msg("Blood Pressure", graph_data)
    second_page_content.extend(analytics_paragraphs)
    second_page_content.append(Image(graph_image_path, width=600, height=290))
    # Add the second page content to the story
    story.extend(second_page_content)

    # Add a page break to start a new page
    story.append(PageBreak())
    

     # Create a new table for blood pressure data
    glucose_data = [
        ["Glucose Readings"],
        ["Date/Time", "Glucose (mg/dL)"], # Leave placeholders for the latest readings
    ]

    # Add rows for the first 5 readings
    for vital in latest_readings:
        glucose_data.append([vital.timestamp, vital.glucose])


    glucose_data.append( ["Baseline", f"{resident.get_baseline([int(vital.glucose) for vital in get_vitals_list_resident(get_selected_resident())] )}"])

    glucose_table = Table(glucose_data, colWidths=[120, 100, 100, 100])

    glucose_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (-1, 0)),  # Span the first row across all columns
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertically center the text
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Make the first row bold
        ('FONTSIZE', (0, 0), (-1, 0), 14),  # Increase the font size for the first row
        ('FONTSIZE', (0, 1), (-1, 1), 12),  # Increase the font size for the first row
        ('FONTSIZE', (0, 2), (-1, -1), 11),  # Adjust the font size as needed
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),  # Add some padding to the bottom of cells
        ('BACKGROUND', (0, 0), (-1, 0), "#003366"),  # Set background color of the first row to "#003366"
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Set text color of the first row to white
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Add grid lines for all cells
        ('GRID', (0, -1), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, 1), "#CCCCCC"),  # Set background color of the second row to "#CCCCCC"
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.black),  # Set text color of the second row to black
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),  # Make the second row bold
         # Make the bottom row bold
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        # Increase the thickness of border lines for the bottom row
        ('GRID', (0, -1), (-1, -1), 3, colors.black),
    ]))
    # Modify the background color based on glucose values
    for i, row in enumerate(glucose_data[2:]):
        glucose_value = float(row[1])
        background_color = get_background_color_glucose(int(glucose_value))
        if background_color:
            glucose_table.setStyle(TableStyle([
                ('BACKGROUND', (0, i + 2), (-1, i + 2), background_color),
            ]))
    
    # Create a new table for the legend
    legend_data1 = [
        ["Legend (2 to 3 hours after eating)","",""],
        ["Normal","Impaired Glucose","Diabetic"],
    ]

    legend_table1 = Table(legend_data1)
    # Set the style for the legend table to show grid lines
    legend_table1.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Add grid lines for all cells
        ('SPAN', (0, 0), (-1, 0)),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Make the first row bold
        ('BACKGROUND', (0, 0), (-1, 0), "#CCCCCC"),  # Set background color of the second row to "#CCCCCC"
        ('BACKGROUND', (0, 1), (0, 1), "#77BB66"),  # Change background color of the first cell in the second row
        ('BACKGROUND', (1, 1), (1, 1), "#F7A64A"),  # Change background color of the second cell in the second row
        ('BACKGROUND', (2, 1), (2, 1), "#F1444A"),  # Change background color of the third cell in the second row

    ]))

    graph_data = resident.check_condition(db.get_medication_list(get_selected_resident()),[int(vital.glucose) for vital in get_vitals_list_resident(get_selected_resident())])

    import plotly.graph_objects as go
    import plotly.io as pio

     # Check if graph_data is an integer
    if isinstance(graph_data, int):
        # Create an empty graph with tables
        fig2 = go.Figure()

        # Add title
        fig2.update_layout(title='No Data Available')

    else:
        # Create figure with secondary y-axis
        fig2 = go.Figure()

        # Plot baseline and systolic BP on the first y-axis
        fig2.add_trace(go.Scatter(x=list(graph_data[3]), y=graph_data[4], mode='lines', name='Baseline', line=dict(color='red', dash='dash')))
        fig2.add_trace(go.Scatter(x=list(graph_data[3]), y=graph_data[7], mode='lines+markers', name='Glucose', line=dict(color='blue')))
        fig2.add_trace(go.Scatter(x=graph_data[5], y=graph_data[1], mode='lines+markers', name='Exceedance Alert', line=dict(color='orange', dash='dash'), marker=dict(color='orange')))

        # Plot medication start dates as vertical lines
        for i, medication in enumerate(graph_data[6]):
            fig2.add_shape(go.layout.Shape(type="line", x0=i, x1=i, y0=0, y1=1, line=dict(color='gray', dash='dash'), xref="x", yref="paper"))
            fig2.add_trace(go.Scatter(x=[0], y=[120], mode='markers', marker=dict(color='gray'), name=f'Medication Start: {medication.name}'))

        # Add first y-axis labels
        fig2.update_layout(
            xaxis=dict(title='Time'),
            yaxis=dict(title='Glucose Levels', side='left', color='blue'),
            legend=dict(x=1.1, y=0.3, traceorder='normal', orientation='h'),
        )

        # Retrieve wellness data for the selected resident
        current_wellness = [wellness for wellness in get_wellness_check_list_resident(resident)]

        # Create a twin Axes for the second y-axis
        fig2.add_trace(go.Scatter(x=list(range(len(current_wellness))), y=[wellness.rating for wellness in current_wellness], mode='lines+markers', name='Wellness Check', line=dict(color='green'), yaxis='y2'))

        fig2.update_layout(
            yaxis2=dict(title='Wellness Check', overlaying='y', side='right', color='green'),
        )

        # Add title and grid
        fig2.update_layout(
            title='Glucose and Wellness Check Correlation',
            title_x=0.2,
            showlegend=True,
        )

    # Save the image
    graph_image_path = r"website\static\images\glucose_image.png"  # Replace with the actual path where you want to save the image
    pio.write_image(fig2, graph_image_path)

    # Add content for the third page (you can customize this according to your needs)
    third_page_content = [
        glucose_table,
        Spacer(1, 20),
        legend_table1,
        Spacer(1, 10),
    ]
    analytics_paragraphs = get_analytics_msg("Glucose", graph_data)
    third_page_content.extend(analytics_paragraphs)
    third_page_content.append(Image(graph_image_path, width=600, height=290))

    # Add the third page content to the story
    story.extend(third_page_content)
      # Add a page break to start a new page
    story.append(PageBreak())

     # Create a new table for blood pressure data
    pulse_data = [
        ["Pulse Readings"],
        ["Date/Time", "Pulse (BPM)"],
    ]

    # Add rows for the first 5 readings
    for vital in latest_readings:
        pulse_data.append([vital.timestamp, vital.heart_rate])


    pulse_data.append( ["Baseline", f"{resident.get_baseline([int(vital.heart_rate) for vital in get_vitals_list_resident(get_selected_resident())] )}"])

    pulse_table = Table(pulse_data, colWidths=[120, 100, 100, 100])

    pulse_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (-1, 0)),  # Span the first row across all columns
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertically center the text
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Make the first row bold
        ('FONTSIZE', (0, 0), (-1, 0), 14),  # Increase the font size for the first row
        ('FONTSIZE', (0, 1), (-1, 1), 12),  # Increase the font size for the first row
        ('FONTSIZE', (0, 2), (-1, -1), 11),  # Adjust the font size as needed
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),  # Add some padding to the bottom of cells
        ('BACKGROUND', (0, 0), (-1, 0), "#003366"),  # Set background color of the first row to "#003366"
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Set text color of the first row to white
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Add grid lines for all cells
        ('GRID', (0, -1), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, 1), "#CCCCCC"),  # Set background color of the second row to "#CCCCCC"
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.black),  # Set text color of the second row to black
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),  # Make the second row bold
         # Make the bottom row bold
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        # Increase the thickness of border lines for the bottom row
        ('GRID', (0, -1), (-1, -1), 3, colors.black),
    ]))
    # Modify the background color based on glucose values
    for i, row in enumerate(pulse_data[2:]):
        pulse_value = float(row[1])
        background_color = get_background_color_pulse(int(pulse_value))
        if background_color:
            pulse_table.setStyle(TableStyle([
                ('BACKGROUND', (0, i + 2), (-1, i + 2), background_color),
            ]))
    
    # Create a new table for the legend
    legend_data2 = [
        ["Legend","",""],
        ["Low","Normal","Mild Tachycardia","Moderate Tachycardia","Severe Tachycardia"],
    ]

    legend_table2 = Table(legend_data2)
    # Set the style for the legend table to show grid lines
    legend_table2.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Add grid lines for all cells
        ('SPAN', (0, 0), (-1, 0)),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Make the first row bold
        ('BACKGROUND', (0, 0), (-1, 0), "#CCCCCC"),  # Set background color of the second row to "#CCCCCC"
        ('BACKGROUND', (0, 0), (-1, 0), "#CCCCCC"),  # Set background color of the second row to "#CCCCCC"
        ('BACKGROUND', (0, 1), (0, 1), "#458CCC"),  # Change background color of the first cell in the second row
        ('BACKGROUND', (1, 1), (1, 1), "#77BB66"),  # Change background color of the second cell in the second row
        ('BACKGROUND', (2, 1), (2, 1), "#F7A64A"),  # Change background color of the third cell in the second row
        ('BACKGROUND', (3, 1), (3, 1), "#F07C7F"),  # Change background color of the fourth cell in the second row
        ('BACKGROUND', (4, 1), (4, 1), "#F1444A"),  # Change background color of the fifth cell in the second row
    ]))

    graph_data = resident.check_condition(db.get_medication_list(get_selected_resident()),[int(vital.heart_rate) for vital in get_vitals_list_resident(get_selected_resident())])

    import plotly.graph_objects as go
    import plotly.io as pio

    # Check if graph_data is an integer
    if isinstance(graph_data, int):
        # Create an empty graph with tables
        fig3 = go.Figure()

        # Add title
        fig3.update_layout(title='No Data Available')

    else:
        # Create figure with secondary y-axis
        fig3 = go.Figure()

        # Plot baseline and systolic BP on the first y-axis
        fig3.add_trace(go.Scatter(x=list(graph_data[3]), y=graph_data[4], mode='lines', name='Baseline', line=dict(color='red', dash='dash')))
        fig3.add_trace(go.Scatter(x=list(graph_data[3]), y=graph_data[7], mode='lines+markers', name='Pulse', line=dict(color='blue')))
        fig3.add_trace(go.Scatter(x=graph_data[5], y=graph_data[1], mode='lines+markers', name='Exceedance Alert', line=dict(color='orange', dash='dash'), marker=dict(color='orange')))

        # Plot medication start dates as vertical lines
        for i, medication in enumerate(graph_data[6]):
            fig3.add_shape(go.layout.Shape(type="line", x0=i, x1=i, y0=0, y1=1, line=dict(color='gray', dash='dash'), xref="x", yref="paper"))
            fig3.add_trace(go.Scatter(x=[0], y=[120], mode='markers', marker=dict(color='gray'), name=f'Medication Start: {medication.name}'))

        # Add first y-axis labels
        fig3.update_layout(
            xaxis=dict(title='Time'),
            yaxis=dict(title='Pulse Levels', side='left', color='blue'),
            legend=dict(x=1.1, y=0.3, traceorder='normal', orientation='h'),
        )

        # Retrieve wellness data for the selected resident
        current_wellness = [wellness for wellness in get_wellness_check_list_resident(resident)]

        # Create a twin Axes for the second y-axis
        fig3.add_trace(go.Scatter(x=list(range(len(current_wellness))), y=[wellness.rating for wellness in current_wellness], mode='lines+markers', name='Wellness Check', line=dict(color='green'), yaxis='y2'))

        fig3.update_layout(
            yaxis2=dict(title='Wellness Check', overlaying='y', side='right', color='green'),
        )

        # Add title and grid
        fig3.update_layout(
            title='Pulse and Wellness Check Correlation',
            title_x=0.2,
            showlegend=True,
        )

    graph_image_path = r"website\static\images\pulse_image.png" # Replace with the actual path where you want to save the image
    pio.write_image(fig3, graph_image_path)

     # Add content for the second page (you can customize this according to your needs)
    fourth_page_content = [
        pulse_table,
        Spacer(1,20),
        legend_table2,
        Spacer(1,10),
    ]

    analytics_paragraphs = get_analytics_msg("Pulse", graph_data)
    fourth_page_content.extend(analytics_paragraphs)
    fourth_page_content.append(Image(graph_image_path, width=600, height=290))
    # Add the second page content to the story
    story.extend(fourth_page_content)
    
    # Add a page break to start a new page
    story.append(PageBreak())
    
     # Create a new table for blood pressure data
    temp_data = [
        ["Temperature Readings"],
        ["Date/Time", "Temperature (F)"], # Leave placeholders for the latest readings
    ]

    # Add rows for the first 5 readings
    for vital in latest_readings:
        temp_data.append([vital.timestamp, vital.temperature])


    temp_data.append( ["Baseline", f"{resident.get_baseline([int(vital.temperature) for vital in get_vitals_list_resident(get_selected_resident())] )}"])

    temp_table = Table(temp_data, colWidths=[120, 100, 100, 100])

    temp_table.setStyle(TableStyle([
        ('SPAN', (0, 0), (-1, 0)),  # Span the first row across all columns
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertically center the text
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Make the first row bold
        ('FONTSIZE', (0, 0), (-1, 0), 14),  # Increase the font size for the first row
        ('FONTSIZE', (0, 1), (-1, 1), 12),  # Increase the font size for the first row
        ('FONTSIZE', (0, 2), (-1, -1), 11),  # Adjust the font size as needed
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),  # Add some padding to the bottom of cells
        ('BACKGROUND', (0, 0), (-1, 0), "#003366"),  # Set background color of the first row to "#003366"
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Set text color of the first row to white
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Add grid lines for all cells
        ('GRID', (0, -1), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 1), (-1, 1), "#CCCCCC"),  # Set background color of the second row to "#CCCCCC"
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.black),  # Set text color of the second row to black
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),  # Make the second row bold
         # Make the bottom row bold
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        # Increase the thickness of border lines for the bottom row
        ('GRID', (0, -1), (-1, -1), 3, colors.black),
    ]))
    # Modify the background color based on glucose values
    for i, row in enumerate(temp_data[2:]):
        temp_value = float(row[1])
        background_color = get_background_color_pulse(int(temp_value))
        if background_color:
            temp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, i + 2), (-1, i + 2), background_color),
            ]))
    
    # Create a new table for the legend
    legend_data3 = [
        ["Legend","",""],
        ["Hypothermia","Normal","Fever","Hyperthermia"],
    ]

    legend_table3 = Table(legend_data3)
    # Set the style for the legend table to show grid lines
    legend_table3.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Add grid lines for all cells
        ('SPAN', (0, 0), (-1, 0)),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Make the first row bold
        ('BACKGROUND', (0, 0), (-1, 0), "#CCCCCC"),  # Set background color of the second row to "#CCCCCC"
        ('BACKGROUND', (0, 0), (-1, 0), "#CCCCCC"),  # Set background color of the second row to "#CCCCCC"
        ('BACKGROUND', (0, 1), (0, 1), "#458CCC"),  # Change background color of the first cell in the second row
        ('BACKGROUND', (1, 1), (1, 1), "#77BB66"),  # Change background color of the second cell in the second row
        ('BACKGROUND', (2, 1), (2, 1), "#F7A64A"),  # Change background color of the third cell in the second row
        ('BACKGROUND', (3, 1), (3, 1), "#F1444A"),  # Change background color of the fifth cell in the second row
    ]))

    graph_data = resident.check_condition(db.get_medication_list(get_selected_resident()),[int(vital.temperature) for vital in get_vitals_list_resident(get_selected_resident())])

    import plotly.graph_objects as go
    import plotly.io as pio
    # Check if graph_data is an integer
    if isinstance(graph_data, int):
        # Create an empty graph with tables
        fig4 = go.Figure()

        # Add title
        fig4.update_layout(title='No Data Available')

    else:
        # Create figure with secondary y-axis
        fig4 = go.Figure()

        # Plot baseline and systolic BP on the first y-axis
        fig4.add_trace(go.Scatter(x=list(graph_data[3]), y=graph_data[4], mode='lines', name='Baseline', line=dict(color='red', dash='dash')))
        fig4.add_trace(go.Scatter(x=list(graph_data[3]), y=graph_data[7], mode='lines+markers', name='Temperature', line=dict(color='blue')))
        fig4.add_trace(go.Scatter(x=graph_data[5], y=graph_data[1], mode='lines+markers', name='Exceedance Alert', line=dict(color='orange', dash='dash'), marker=dict(color='orange')))

        # Plot medication start dates as vertical lines
        for i, medication in enumerate(graph_data[6]):
            fig4.add_shape(go.layout.Shape(type="line", x0=i, x1=i, y0=0, y1=1, line=dict(color='gray', dash='dash'), xref="x", yref="paper"))
            fig4.add_trace(go.Scatter(x=[0], y=[120], mode='markers', marker=dict(color='gray'), name=f'Medication Start: {medication.name}'))

        # Add first y-axis labels
        fig4.update_layout(
            xaxis=dict(title='Time'),
            yaxis=dict(title='Temperature Levels', side='left', color='blue'),
            legend=dict(x=1.1, y=0.3, traceorder='normal', orientation='h'),
        )

        # Retrieve wellness data for the selected resident
        current_wellness = [wellness for wellness in get_wellness_check_list_resident(resident)]

        # Create a twin Axes for the second y-axis
        fig4.add_trace(go.Scatter(x=list(range(len(current_wellness))), y=[wellness.rating for wellness in current_wellness], mode='lines+markers', name='Wellness Check', line=dict(color='green'), yaxis='y2'))

        fig4.update_layout(
            yaxis2=dict(title='Wellness Check', overlaying='y', side='right', color='green'),
        )

        # Add title and grid
        fig4.update_layout(
            title='Temperature and Wellness Check Correlation',
            title_x=0.2,
            showlegend=True,
        )

    graph_image_path = r"website\static\images\temp_image.png" # Replace with the actual path where you want to save the image
    pio.write_image(fig4, graph_image_path)

     # Add content for the second page (you can customize this according to your needs)
    fifth_page_content = [
        temp_table,
        Spacer(1,20),
        legend_table3,
        Spacer(1,10),
    ]

    analytics_paragraphs = get_analytics_msg("Temperature", graph_data)
    fifth_page_content.extend(analytics_paragraphs)
    fifth_page_content.append(Image(graph_image_path, width=600, height=290))

    # Add the second page content to the story
    story.extend(fifth_page_content)

    # Build the PDF document
    doc.build(story)

    # Reset the buffer position to the beginning
    buffer.seek(0)

    # Return the buffer containing the PDF data
    return buffer

#Get the conecentration of a medicaiton for a specific resident
# Return the concentration values
def concen(medication,resident):
    from datetime import timedelta
    import math
    graph_data = db.get_graph10_data(medication, resident)
    up_to = len(graph_data['DateTime'])-1
    # Define the time intervals as datetime objects
    if graph_data['DateTime']:
        start_time = graph_data['DateTime'][0]  # Start time
        end_time = graph_data['DateTime'][up_to]   # End time
        intake_timestamps = graph_data['DateTime'][:up_to]
    else:
        intake_timestamps = []
        start_time = datetime(2023, 1, 1, 0, 0)  # Start time
        end_time = datetime(2023, 1, 7, 0, 0)

    # Create a list of timestamps from start_time to end_time at the specified interval
    time_stamps = [start_time + timedelta(hours=i) for i in range(0, int((end_time - start_time).total_seconds() // 3600))]
    
    # Define the drug's half-life in hours
    half_life_hours = float(medication.half_life) 

    # Calculate the decay rate based on half-life
    decay_rate = math.log(1/2) / half_life_hours
    
    # Create a function to calculate drug concentration over time with spikes for each intake
    def calculate_concentration(time_stamps, decay_rate, intake_timestamps):
        current_concentration = 0.0

        # Define a time step factor to control the rate of decay
        time_step_factor = 0.9  # Adjust as needed; smaller values result in slower decay
        concen_before_spike = []
        for t in time_stamps:
            # Check if there is an intake event at this time
            if any(
                t.hour == ts.hour and t.day == ts.day and t.month == ts.month and t.year == ts.year
                for ts in intake_timestamps
            ):
                concen_before_spike.append(current_concentration)
                current_concentration = 100.0  # Spike to 100% when intake occurs

            # Apply decay with a controlled time step
            current_concentration *= math.exp(decay_rate * time_step_factor)

        return concen_before_spike

    # Calculate drug concentrations over time using the updated function
    concentration_values = calculate_concentration(time_stamps, decay_rate, intake_timestamps)
    return concentration_values

#Creates the auto generated message based on the condition that will appear on the comprehensive medical report
def get_analytics_msg(condition,data):
    #Checks if there is data to report
    if isinstance(data, int):
        return [Paragraph(f"There is not enough data for an analysis. Please enter more vitals for {condition}.")]

    #Gets all the information related to the vitals
    vitals = data[7]
    spike_index = data[5]
    timestamps = data[8]
    baseline = data[4]

    resident = get_selected_resident()
    date_min = min(time for time in timestamps)
    date_max = max(time for time in timestamps)
    medication_list = get_medication_list_resident(resident)

    check_condition = "An error happened"
    aonec_levels = 0
    aonec_msg = ""
    currently_taken = []
    condition_medication_list = []
    adherence = 0
    mar = 0
    expected = ""
    status = ""
    unit = ""
    
    #Checks which condition is being used and create the custom message for that condtion
    if condition == "Blood Pressure":
        unit = " mmHg"
        baseline_msg = str(resident.get_baseline([int(vital.systolic_blood_pressure) for vital in resident.get_vitals_list()]))
        baseline_msg += " / " + str(resident.get_baseline([int(vital.diastolic_blood_pressure) for vital in resident.get_vitals_list()]))
        baseline_msg += unit
        check_condition = resident.check_blood_pressure()
    elif condition == "Glucose":
        unit = " mg/dL"
        baseline_msg = str(resident.get_baseline([int(vital.glucose) for vital in resident.get_vitals_list()])) + unit
        check_condition = resident.check_glucose()
        aonec_levels = resident.calculate_A1C()
        aonec_msg = f" with A1C Levels of {aonec_levels}%"
    elif condition == "Pulse":
        unit = " BPM"
        baseline_msg = str(resident.get_baseline([int(vital.heart_rate) for vital in resident.get_vitals_list()])) + unit
        check_condition = resident.check_heart_rate()
    elif condition == "Temperature":
        unit = "&deg;F"
        baseline_msg = str(resident.get_baseline([int(vital.temperature) for vital in resident.get_vitals_list()]))
        baseline_msg += unit
        check_condition = resident.check_temp()

    paragraphs = []

    analytic_info = f"An analysis of <b>{resident.first_name}'s</b> data related to {condition} shows the following characteristics. <br/>For the period from <b>{date_min.strftime('%B')} {date_min.day}</b> to <b>{date_max.strftime('%B')} {date_max.day}</b> the baseline {condition} is <b>{baseline_msg}{aonec_msg}</b>.<br/>"
    paragraphs.append(Paragraph(analytic_info))

    #If there is a big anamoly in the data then create a section of the paragragh for that.
    if any(spike_index):
        spike_msg = f"<b>Spikes</b> that could warrant investigation; at "
        for i, index in enumerate(spike_index):
            try:
                spike_msg += f"{timestamps[index].strftime('%b')} {timestamps[index].day} with a value of <b>{vitals[index]}{unit}</b>"
        
                # Add a comma if the current item is not the last one
                if i < len(spike_index) - 1:
                    spike_msg += ", "
                else:
                    spike_msg += ".<br/><br/>"
            except IndexError as e:
                continue

        paragraphs.append(Paragraph(spike_msg))

    
    #Gets the medication that were started this month and list them
    for medication in medication_list:
        current_date = datetime.now()
        if (medication.start_date.year == current_date.year and medication.start_date.month == current_date.month):
            currently_taken.append(medication)
    analytic_info = f"Data analytics shows that {resident.first_name}"
   
    condition_medication_list = resident.medication_condition(condition, medication_list)

    #If the resident is taking medicaiton for said condition then label it and show that stats for that medication
     # Retrieves all the analytics and statistics associated with a that medication 
    if any(condition_medication_list):
        adherence_msg = f"Analyzing Medication Adherence for {condition} reveals that <br/>"
        shown_conditions = []
        for medication in condition_medication_list:
            if(medication.name not in shown_conditions):
                shown_conditions.append(medication.name)
                adherence = db.get_graph4_data(medication, get_selected_resident())["Average"]
                if len(adherence) >=3:
                    mar = round(sum(adherence) / len(adherence), 2)
                    if (mar >= 80.00):
                        expected = "above"
                    else:
                        expected = "below"

                    missed_dose = adherence.count(0)
                    daily_dose = db.get_graph8_data(medication, resident)["Dose (mg)"]
                    daily_dose_avg = round(sum(float(dose) for dose in daily_dose) / len(daily_dose),2)
                    half_life_msg = ""
                    if missed_dose > 0:
                        avg_concentration = 0
                        min_concentration = 0
                        concentration_list = concen(medication,get_selected_resident())
                        min_concentration = min(concentration_list)
                        concentration_list.remove(min_concentration)
                        if len(concentration_list) != 0:
                            avg_concentration = round(sum(concentration_list)/len(concentration_list),2)
                            half_life_msg = f" Since doses were missed the average <b>lowest drug concentration in the body was {avg_concentration}%</b> with the <b>lowest concentration being {min_concentration}%</b>. This could affect treatment effectiveness."
            
                    adherence_msg += f"<br/><b>{medication.name}</b> has {mar}% adherence. This is <b>{expected} the accepted threshold of 80%</b>. There were <b>{missed_dose}</b> missed doses during the period."
                    adherence_msg += f" The average daily dose was <b>{daily_dose_avg} mg</b>.{half_life_msg}<br/>"
                else:
                    adherence_msg += f"<b>There is not enough data on {medication.name} to provide an accurate analysis</b><br/>"

        paragraphs.append(Paragraph(adherence_msg))

    #Traverses the baseline and finds out if its increasing, decreasing or is stable
    increasing = all(baseline[i] <= baseline[i + 1] for i in range(len(baseline) - 1))
    decreasing = all(baseline[i] >= baseline[i + 1] for i in range(len(baseline) - 1))

    #Prints the message based on the result
    if increasing:
        status = "not getting better with the current treatment."
    elif decreasing:
        status = " getting better with the current treatment."
    else:
        status = " stable with the current treatment"

    status_msg = f"<br/>Based on the baseline the data shows that <b>{resident.first_name}'s {condition} is considered <em>{check_condition}</em></b>. "
    status_msg += f"Historical data analysis shows that {resident.first_name} is <b>{status}</b>"
    paragraphs.append(Paragraph(status_msg))

    return paragraphs

#Generates the qr code with the residents image in the center
def generate_qr_with_logo(url,resident):
    from PIL import Image
    import requests
    from io import BytesIO

    image_url = resident.get_image()
    # Send a GET request to the URL
    response = requests.get(image_url)

    # Load logo image
    logo = Image.open(BytesIO(response.content))

    # Resize the logo
    basic = 100
    width_percentage = (basic / float(logo.size[0]))
    height_size = int((float(logo.size[1]) * float(width_percentage)))
    logo = logo.resize((basic, height_size))

    # Create QR code
    qrc = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qrc.add_data(url)
    qrc.make()
    qr_img = qrc.make_image(fill_color='black', bg_color="#fff").convert('RGBA')

    # Calculate position for logo in the center
    position = ((qr_img.size[0] - logo.size[0]) // 2, (qr_img.size[1] - logo.size[1]) // 2)

    # Paste the logo onto the QR code
    qr_img.paste(logo, position)

    return qr_img




# Define the header method
def header(canvas, doc, name,type):
    canvas.saveState()
    current_page = canvas.getPageNumber()

    page_width, page_height = doc.pagesize
    # Draw a blue background for the header
    canvas.setFillColor(colors.HexColor("#003366"))
    canvas.rect(0, page_height - 60, page_width, 60, fill=True)
    
    
    # Set the stroke color for the red line
    canvas.setStrokeColor(colors.red)
    canvas.setLineWidth(2)
    # Draw a red line only at the bottom
    canvas.line(0, page_height - 60, page_width, page_height - 60)


    # Draw a gray box directly under the red line
    canvas.setFillColor(colors.HexColor("#CCCCCC"))
    canvas.setStrokeColor(colors.HexColor("#CCCCCC"))
    canvas.rect(0, page_height - 92, page_width, 30, fill=True)

     # Draw the header text in yellow color ("CareBeat")
    canvas.setFillColor(colors.HexColor("#FFEE99"))
    canvas.setFont('Helvetica-Bold', 30)
    text = "CareBeat"
    text_width = canvas.stringWidth(text, 'Helvetica-Bold', 30)
    canvas.drawString((page_width - text_width) / 2, page_height - 30, text)

    # Add the "Your Caring Companion" text inside the blue box
    canvas.setFillColor(colors.HexColor("#FFFFFF"))
    canvas.setFont('Helvetica', 11)
    subtext = "Your Caring Companion"
    subtext_width = canvas.stringWidth(subtext, 'Helvetica', 11)
    canvas.drawString((page_width - subtext_width) / 2, page_height - 50, subtext)
    if current_page == 1:
        # Draw the header text in yellow color ("CareBeat")
        canvas.setFillColor(colors.black)
        canvas.setFont('Helvetica-Bold', 16)
        text = f"{name}'s Medication {type}"
        text_width = canvas.stringWidth(text, 'Helvetica-Bold', 16)
        canvas.drawString((page_width - text_width) / 2, page_height - 82, text)

        if type == "Report":
            # Draw a gray box directly under the red line
            canvas.setFillColor(colors.HexColor("#CCCCCC"))
            canvas.setStrokeColor(colors.HexColor("#CCCCCC"))
            canvas.rect(0, page_height - 250, page_width, 30, fill=True)
            # Draw the header text in yellow color ("CareBeat")
            canvas.setFillColor(colors.black)
            canvas.setFont('Helvetica-Bold', 16)
            text = "Medication List"
            text_width = canvas.stringWidth(text, 'Helvetica-Bold', 16)
            canvas.drawString((page_width - text_width) / 2, page_height - 240, text)



        # Get the current date and time
        current_datetime = datetime.now()
        current_datetime_str = current_datetime.strftime("%B %d, %Y | %I:%M %p")

        # Draw the current date and time in the top right corner
        canvas.setFillColor(colors.white)
        canvas.setFont('Helvetica', 12)
        date_time_width = canvas.stringWidth(current_datetime_str, 'Helvetica', 12)
        canvas.drawString(page_width - date_time_width - 5, page_height - 18, current_datetime_str)


        
    if current_page >=2:
        # Draw the header text in yellow color ("CareBeat")
        canvas.setFillColor(colors.black)
        canvas.setFont('Helvetica-Bold', 16)
        text = "Vitals and Baseline"
        text_width = canvas.stringWidth(text, 'Helvetica-Bold', 16)
        canvas.drawString((page_width - text_width) / 2, page_height - 84, text)


    canvas.restoreState()

#Executes the QR Code 
def create_qr_codes(resident_list):
    # Create a BytesIO buffer to store the PDF content
    pdf_buffer = BytesIO()

    # Create a PDF document
    c = canvas.Canvas(pdf_buffer, pagesize=letter)

    # Loop through each resident in the list
    for resident in resident_list:
        # Calculate the center of the page
        width, height = letter
        center_x = width / 2
        center_y = height / 2

        # Generate QR code with logo
        qr_img = generate_qr_with_logo(f"http://{config.DOMAIN}:{config.PORT}/qr-medication/{resident.id}",resident)

        # Calculate position for QR code
        qr_x = center_x - qr_img.width / 2
        qr_y = center_y - qr_img.height / 2

        # Draw QR code on the PDF
        c.drawInlineImage(qr_img, qr_x, qr_y)

    # Draw resident name below the QR code with underline
        c.setFont("Helvetica-Bold", 30)  # Use a bigger and bold font
        name = resident.get_full_name()
        text_width = c.stringWidth(name, "Helvetica-Bold", 30)
        text_x = center_x - text_width / 2
        text_y = center_y + qr_img.height / 2 + 10
        text_object = c.beginText(text_x, text_y)
        text_object.setFont("Helvetica-Bold", 30)
        text_object.textLine(name)
        underline_width = text_width
        text_object.textLine("-" * int(underline_width/10))  # Add a space before the underline
        c.drawText(text_object)
        # Add a page break for the next resident
        c.showPage()

    # Save the PDF content to the buffer
    c.save()

    # Reset the buffer position to the beginning
    pdf_buffer.seek(0)

    return pdf_buffer

def get_care_info():
    return db.get_caretaker_phone_email()