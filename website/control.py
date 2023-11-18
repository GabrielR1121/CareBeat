from flask import session
import pickle
from website.config import db
from .models import Wellness_check,Vitals
from flask_login import current_user
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle, Paragraph, PageTemplate,Frame, BaseDocTemplate,Image,Spacer,PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import datetime
import secrets
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .models import Caretaker
from datetime import datetime

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
            for medication in db.get_medication_list(selected_resident):
                if int(id) == medication.id:
                    set_selected_medication(medication)
                    break

def med_administered(med_id):
    for medication in get_medication_list_resident(get_selected_resident()):
        if int(med_id) == medication.id:
            db.insert_into_pill(medication,get_selected_resident(),get_selected_user())
            print("medication was administered")
            break
def get_resident_list(user):
    return db.get_residents(user)

def insert_new_medication(medication_name,route,dosage,pill_quantity,pill_frequency,refill_quantity,start_date,prescription_date,description):
    id = db.find_med_id(medication_name)

    db.add_new_medication(
        get_selected_resident(),
        id,
        medication_name,
        route,
        dosage,
        pill_quantity,
        pill_frequency,
        refill_quantity,
        start_date,
        prescription_date,
    )

def insert_wellness_check(feeling, description, temperature,weight,systolic_bp,diastolic_bp,heart_rate,glucose):
    vitals = None
    
    if any([temperature, weight,systolic_bp, diastolic_bp, heart_rate, glucose]):
        vitals = Vitals(temperature= temperature, weight = weight,systolic_blood_pressure=systolic_bp,diastolic_blood_pressure=diastolic_bp,heart_rate=heart_rate,glucose=glucose)

    wellness = Wellness_check( rating = feeling, description= description)
    db.insert_wellness_check(wellness,get_selected_resident(),vitals)

def get_medication_list_resident(resident):
    return db.get_medication_list(resident)

def get_vitals_list_resident(resident):
    return db.get_vitals(resident)

def get_wellness_check_list_resident(resident):
    return db.get_wellness_checks(resident)

def get_all_medication_names():
    return db.get_all_medication_names()

def generate_password(length=12):
    # Define characters to include in the password
    characters = string.ascii_letters + string.digits + string.punctuation
    
    # Use secrets module to generate a secure random password
    password = ''.join(secrets.choice(characters) for _ in range(length))
    
    return password


def send_email(first_name, last_name,password, to_email):
    # Your email credentials and SMTP server information
    sender_email = "carebeat031@gmail.com"
    sender_password = "Carebeat1234"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587


    subject = "Welcome to CareBeat!"
    body = "Welcome to CareBeat {first_name} {last_name}!\n Your login credentials are,\n Username:{to_email}\nPassword:{password}"

    # Create the email message
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = to_email
    message['Subject'] = subject

    # Attach the body of the email
    message.attach(MIMEText(body, 'plain'))

    # Connect to the SMTP server
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        # Start TLS for security
        server.starttls()

        # Login to the email account
        server.login(sender_email, sender_password)

        # Send the email
        server.sendmail(sender_email, to_email, message.as_string())

    print(f"Email sent to {to_email} successfully!")


def create_new_caretaker(email, first_name,initial, paternal_last_name, maternal_last_name, phone_number):

    password = generate_password(10)
    id = db.create_new_caretaker(email, password ,first_name,initial, paternal_last_name, maternal_last_name, phone_number)

    set_selected_caretaker(Caretaker("Caretaker", id,first_name,email,password,initial,paternal_last_name,maternal_last_name,phone_number,"T-Mobil",5000))

    #send_email(first_name,paternal_last_name,password,email)
    pass
def create_new_resident(first_name,initial,paternal_last_name,maternal_last_name,image,birthday,height):
    db.create_new_resident(first_name,initial,paternal_last_name,maternal_last_name,image,birthday,height,get_selected_caretaker().id,get_selected_caretaker().nursing_home_id)


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
            ['Medication Name', 'Dosage','I take this for' ,'Morning\n(6 am - 10am)', 'Noon\n(11 am - 1 pm)', 'Evening\n(2 pm - 7 pm)', 'Bedtime\n(8 pm - 5 am)']]

    for medication in db.get_medication_list(resident):
        test = []  # Create a new list for each medication
        for diagnostic in medication.get_diagnosis_list():
            test.append(diagnostic.name + " ")
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
    elif 90 <= systolic <= 120 and 60 <= diastolic <= 80:
        return '#77BB66'
    elif 120 <= systolic <= 140 and 80 <= diastolic <= 90:
        return '#F7A64A'
    elif 140 <= systolic <= 160 and 90 <= diastolic <= 100:
        return '#F07C7F'
    elif systolic > 160 or diastolic > 100:
        return '#F1444A'
    
# Function to determine the background color based on blood pressure values
def get_background_color_glucose(glucose):
    if 99 <= glucose <= 140:
        return '#77BB66'
    elif 140 <= glucose <= 160:
        return '#F7A64A'
    else:
        return '#F1444A'
       
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
    image_path = resident.get_image()  # Replace with the actual path to your image file
    image = Image(image_path, width=100, height=100)  # Adjust the width and height as needed

    # Create a table with one row and four columns
    data = [
        [image,
        Paragraph(f"<b>Full Name:</b> {resident.get_full_name()}", styles['Normal']),
        Paragraph(f"<b>Age:</b> {resident.get_age()}", styles['Normal']),
        Paragraph(f"<b>Date of Birth:</b> {resident.birthday}", styles['Normal']),
        Paragraph(f"<b>Weight:</b> {0} kg", styles['Normal'])
        ]
    ]

    table = Table(data, colWidths=[110, doc.width - 400, 80, 100, 70], rowHeights=[110])

    # Style the table to align the image to the left and text with the upper border of the image
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('VALIGN', (0, 0), (0, 0), 'TOP'),
        ('VALIGN', (1, 0), (4, 0), 'TOP'),
    ]))

    # Add the table to the story
    story.append(table)


    # Add a Spacer (optional) to create some space between the table and the rectangle
    story.append(Spacer(1, 50))  # Adjust the space as needed\

    title = Paragraph("All Medications", styles['Title'])
    # Define data dynamically using a for loop
    data = [[title,'','','','',''],
            ['Medication Name', 'Dosage','I take this for' ,'Morning\n(6 am - 10am)', 'Noon\n(11 am - 1 pm)', 'Evening\n(2 pm - 7 pm)', 'Bedtime\n(8 pm - 5 am)']]

    for medication in db.get_medication_list(resident):
        test = []  # Create a new list for each medication
        for diagnostic in medication.get_diagnosis_list():
            test.append(diagnostic.name + " ")
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
    # Add a page break to start a new page
    story.append(PageBreak())



    # Create a PageTemplate for the custom header and section
    header_frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height - 100, id='header')
    header_template = PageTemplate(id='header', frames=[header_frame], onPage=lambda canvas, doc: header(canvas, doc, resident.get_full_name(), "Report"))
    doc.addPageTemplates([header_template])

     # Create a new table for blood pressure data
    bp_data = [
        ["Blood Pressure & Heart Rate Readings"],
        ["Date/Time", "Systolic", "Diastolic","Pulse"], # Leave placeholders for the latest readings
    ]

    # Assuming get_vitals_list_resident returns a list of vital readings
    vitals_list = get_vitals_list_resident(get_selected_resident())
    # Get the latest 6 readings based on timestamp
    latest_readings = sorted(vitals_list, key=lambda x: x.timestamp, reverse=True)[:5]

    for vital in latest_readings:
        bp_data.append([vital.timestamp, vital.systolic_blood_pressure, vital.diastolic_blood_pressure, vital.heart_rate])

    bp_data.append( ["Baseline", f"{resident.get_baseline([systolic.systolic_blood_pressure for systolic in get_vitals_list_resident(get_selected_resident())])}", f"{resident.get_baseline([diastolic.diastolic_blood_pressure for diastolic in resident.get_vitals_list()])}", f"{resident.get_baseline([heart_rate.heart_rate for heart_rate in resident.get_vitals_list()])}"])

    bp_table = Table(bp_data, colWidths=[120, 100, 100, 100])
    

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
    
    # Retrieve wellness data for the selected resident
    current_wellness = [wellness for wellness in get_wellness_check_list_resident(get_selected_resident())
                        if wellness.timestamp.year == datetime.now().year and wellness.timestamp.month == datetime.now().month]

    # Extract date range for wellness analysis
    date_min = min(wellness.timestamp for wellness in current_wellness)
    date_max = max(wellness.timestamp for wellness in current_wellness)

    # Generate paragraph about baseline blood pressure
    analytic_info = f"An analysis of {resident.first_name}'s data related to blood pressure shows the following characteristics. For the period from {date_min.strftime('%b %d')} to {date_max.strftime('%b %d')}, the baseline blood pressure is {resident.get_baseline([systolic.systolic_blood_pressure for systolic in resident.get_vitals_list()])} / {resident.get_baseline([diastolic.diastolic_blood_pressure for diastolic in resident.get_vitals_list()])} with a heart rate of {resident.get_baseline([vital.heart_rate for vital in resident.get_vitals_list()])} bpm."

    # Analyze currently taken medications
    currently_taken = [medication for medication in get_medication_list_resident(resident)
                    if medication.start_date.year == datetime.now().year and medication.start_date.month == datetime.now().month]

    if currently_taken:
        analytic_info += f" {resident.first_name} has been taking: {', '.join([medication.name for medication in currently_taken])}."
    else:
        analytic_info += f" {resident.first_name} has not started any medication during the last month."

    # Analyze average wellness check
    avg_rating = round(sum([wellness.rating for wellness in current_wellness]) / len(current_wellness), 1)
    analytic_info += f" Also, the Average Wellness Check during the month was {avg_rating} out of 5 with 1 being the best possible status and 5 the worst."

    # Analyze blood pressure medication adherence
    bp_medication = resident.medication_condition(resident.check_blood_pressure(), "BP", get_medication_list_resident(resident))

    if bp_medication:
        analytic_info += f" Medication Adherence Analysis for medication taken for blood pressure shows that {bp_medication[0].name} has 86.4% adherence. This is above the accepted threshold of 80%. There were 2 missed doses during the period."
        # daily_dose = db.get_graph8_data(resident, bp_medication[0])["Dose (mg)"]
        # analytic_info += f" The average daily dose was {sum(daily_dose) / (len(daily_dose) + 1)}."

    analytic_info += f" Based on the baseline values, {resident.first_name}'s blood pressure is considered {resident.check_blood_pressure()}. Please refer to the graphics below for a visual representation of the above discussion."
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

    # Create figure with secondary y-axis
    fig = go.Figure()

    # Plot baseline and systolic BP on the first y-axis
    fig.add_trace(go.Scatter(x=list(graph_data[3]), y=graph_data[4], mode='lines', name='Baseline', line=dict(color='red', dash='dash')))
    fig.add_trace(go.Scatter(x=list(graph_data[3]), y=graph_data[7], mode='lines+markers', name='Blood Pressure', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=graph_data[5], y=graph_data[1], mode='lines+markers', name='Exceedance Alert', line=dict(color='orange', dash='dash'), marker=dict(color='orange')))

  # Plot medication start dates as vertical lines
    for i, medication in enumerate(graph_data[6]):
            fig.add_shape(go.layout.Shape(type="line",x0=i,x1=i,y0=0,y1=1,line=dict(color='gray', dash='dash'),xref="x",yref="paper"))
            fig.add_trace(go.Scatter(x=[0],y=[120], mode='markers', marker=dict(color='gray'), name=f'Medication Start: {medication.name}'))

        # Add first y-axis labels
    fig.update_layout(
            xaxis=dict(title='Time'),
            yaxis=dict(title='Blood Pressure Levels', side='left', color='blue'),
            legend=dict(x=1.1, y=0.3, traceorder='normal', orientation='h'),
        )

    # Create a twin Axes for the second y-axis
    fig.add_trace(go.Scatter(x=list(range(len(current_wellness))), y=[wellness.rating for wellness in current_wellness], mode='lines+markers', name='Wellness Check', line=dict(color='green'), yaxis='y2'))

    fig.update_layout(
        yaxis2=dict(title='Wellness Check', overlaying='y', side='right', color='green'),
    )


    # Add title and grid
    fig.update_layout(
        title='Blood Pressure and Wellness Check Correlation',
        title_x = 0.2,
        showlegend=True,
       # grid=dict(True),
    )
    graph_image_path = r"website\static\images\bp_image.png" # Replace with the actual path where you want to save the image
    pio.write_image(fig, graph_image_path)

    # Add content for the second page (you can customize this according to your needs)
    second_page_content = [
        bp_table,
        Spacer(1,20),
        legend_table,
        Spacer(1,10),
        Paragraph(analytic_info, centered_style),
        Image(graph_image_path, width=600, height=290),
    ]

    # Add the second page content to the story
    story.extend(second_page_content)

    # Add a page break to start a new page
    story.append(PageBreak())
    

     # Create a new table for blood pressure data
    glucose_data = [
        ["Glucose Readings"],
        ["Date/Time", "Glucose"], # Leave placeholders for the latest readings
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

    analytic_info = ""

    # Add a paragraph about baseline blood pressure
    analytic_info = f"An analysis of {resident.first_name}'s data related to Glucose shows the following characteristics. For the period from {date_min.strftime('%b')} {date_min.day} to {date_max.strftime('%b')} {date_max.day} the baseline glucose is {resident.get_baseline([int(vital.glucose) for vital in resident.get_vitals_list()])} mg/dL."+ f"Data analytics shows that {resident.first_name}"
    currently_taken = []
    for medication in get_medication_list_resident(resident):
        current_date = datetime.now()
        if (medication.start_date.year == current_date.year and medication.start_date.month == current_date.month):
           currently_taken.append(medication)
    if currently_taken:
        analytic_info += " has been taking"
        analytic_info += ", ".join([medication.name for medication in currently_taken])
    else:
        analytic_info += " has not started any medication"
    analytic_info += ' during the last month.'

   
    

    analytic_info += f" Also, the Average Wellness Check during the month was {round(sum([wellness.rating for wellness in current_wellness])/len([wellness.rating for wellness in current_wellness]),1)} out of 5 with 1 being the best possible status and 5 the worst."


    
    
    glucose_medication = resident.medication_condition(resident.check_glucose(),"glucose" ,get_medication_list_resident(resident))
    #adherence = db.get_graph4_data(get_selected_resident(),bp_medication[0])["Average"]
    if glucose_medication:
        analytic_info += f" Medication Adherence Analysis for medication taken for glucose shows that {glucose_medication[0].name} has {90.2}% adherence.  This is above the accepted threshold of 80%. There were {1} missed doses during the period."
        daily_dose = db.get_graph8_data(resident,bp_medication[0])["Dose (mg)"]
        # analytic_info += f" The average daily dose was {sum(daily_dose)/(len(daily_dose)+1)}."

    analytic_info += f" Based on the baseline values {resident.first_name}'s glucose is considered {resident.check_glucose()}.Please refer to the graphics below for a visual representation of the above discussion."
    



    graph_data = resident.check_condition(db.get_medication_list(get_selected_resident()),[int(vital.glucose) for vital in get_vitals_list_resident(get_selected_resident())])

    import plotly.graph_objects as go
    import plotly.io as pio

    # Create figure with secondary y-axis
    fig2 = go.Figure()

    # Plot baseline and systolic BP on the first y-axis
    fig2.add_trace(go.Scatter(x=list(graph_data[3]), y=graph_data[4], mode='lines', name='Baseline', line=dict(color='red', dash='dash')))
    fig2.add_trace(go.Scatter(x=list(graph_data[3]), y=graph_data[7], mode='lines+markers', name='Glucose Levels', line=dict(color='blue')))
    fig2.add_trace(go.Scatter(x=graph_data[5], y=graph_data[1], mode='lines+markers', name='Exceedance Alert', line=dict(color='orange', dash='dash'), marker=dict(color='orange')))

  # Plot medication start dates as vertical lines
    for i, medication in enumerate(graph_data[6]):
            fig2.add_shape(go.layout.Shape(type="line",x0=i,x1=i,y0=0,y1=1,line=dict(color='gray', dash='dash'),xref="x",yref="paper"))
            fig2.add_trace(go.Scatter(x=[0],y=[120], mode='markers', marker=dict(color='gray'), name=f'Medication Start: {medication.name}'))

        # Add first y-axis labels
    fig2.update_layout(
            xaxis=dict(title='Time'),
            yaxis=dict(title='Glucose Level', side='left', color='blue'),
            legend=dict(x=1.1, y=0.3, traceorder='normal', orientation='h'),
        )

    # Create a twin Axes for the second y-axis
    fig2.add_trace(go.Scatter(x=list(range(len(current_wellness))), y=[wellness.rating for wellness in current_wellness], mode='lines+markers', name='Wellness Check', line=dict(color='green'), yaxis='y2'))

    fig2.update_layout(
        yaxis2=dict(title='Wellness Check', overlaying='y', side='right', color='green'),
    )


    # Add title and grid
    fig2.update_layout(
        title='Glucose and Wellness Check Correlation',
        title_x = 0.2,
        showlegend=True,
       # grid=dict(True),
    )
    graph_image_path = r"website\static\images\glucose_image.png" # Replace with the actual path where you want to save the image
    pio.write_image(fig2, graph_image_path)

     # Add content for the second page (you can customize this according to your needs)
    third_page_content = [
        glucose_table,
        Spacer(1,20),
        legend_table1,
        Spacer(1,10),
        Paragraph(analytic_info, centered_style),
        Image(graph_image_path, width=600, height=290),
    ]

    # Add the second page content to the story
    story.extend(third_page_content)
    # Build the PDF document
    doc.build(story)

    # Reset the buffer position to the beginning
    buffer.seek(0)

    # Return the buffer containing the PDF data
    return buffer

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

       

        # Get the current date and time
        current_datetime = datetime.now()
        current_datetime_str = current_datetime.strftime("%B %d, %Y | %I:%M %p")

        # Draw the current date and time in the top right corner
        canvas.setFillColor(colors.white)
        canvas.setFont('Helvetica', 12)
        date_time_width = canvas.stringWidth(current_datetime_str, 'Helvetica', 12)
        canvas.drawString(page_width - date_time_width - 5, page_height - 18, current_datetime_str)

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
        
    if current_page in [2,3,4,5]:
        # Draw the header text in yellow color ("CareBeat")
        canvas.setFillColor(colors.black)
        canvas.setFont('Helvetica-Bold', 16)
        text = "Vitals and Baseline"
        text_width = canvas.stringWidth(text, 'Helvetica-Bold', 16)
        canvas.drawString((page_width - text_width) / 2, page_height - 84, text)


    canvas.restoreState()