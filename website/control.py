from flask import session
import pickle
from website.config import db
from flask_login import current_user

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