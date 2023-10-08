from flask import session
import pickle
from website.config import db
from flask_login import current_user
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle, Paragraph, PageTemplate,Frame, BaseDocTemplate
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import datetime

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
            ['Medication Name', 'Dosage', 'Morning\n(6 am - 10am)', 'Noon\n(11 am - 1 pm)', 'Evening\n(2 pm - 7 pm)', 'Bedtime\n(8 pm - 5 am)']]

    for medication in resident.get_medication_list():
        data.append([medication.name,medication.dosage,medication.morning_bool,medication.noon_bool,medication.evening_bool, medication.bedtime_bool])


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
    ]))

    story.append(table)

    # Create a Spacer to separate the table from the footer note
    footer_note = Paragraph("<font color='#888888'>Displays medication intake analysis, not the prescribed one.</font>", styles['Normal'])

    story.append(footer_note)

    # Create a PageTemplate for the custom header
    header_frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height - 100, id='header')
    header_template = PageTemplate(id='Page', frames=[header_frame], onPage=lambda canvas, doc: header(canvas, doc, resident.get_full_name()))
    doc.addPageTemplates([header_template])

    # Build the PDF document
    doc.build(story)

    # Reset the buffer position to the beginning
    buffer.seek(0)

    # Return the buffer containing the PDF data
    return buffer



# Define the header method
def header(canvas, doc, name):
    canvas.saveState()
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
    canvas.setFillColor(colors.black)
    canvas.setFont('Helvetica-Bold', 16)
    text = f"{name}'s Medication List"
    text_width = canvas.stringWidth(text, 'Helvetica-Bold', 16)
    canvas.drawString((page_width - text_width) / 2, page_height - 82, text)

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

    # Get the current date and time
    current_datetime = datetime.datetime.now()
    current_datetime_str = current_datetime.strftime("%B %d, %Y | %I:%M %p")

    # Draw the current date and time in the top right corner
    canvas.setFont('Helvetica', 12)
    date_time_width = canvas.stringWidth(current_datetime_str, 'Helvetica', 12)
    canvas.drawString(page_width - date_time_width - 5, page_height - 18, current_datetime_str)

    canvas.restoreState()