from flask_login import UserMixin

class Resident:
    '''
    Class for the Resident
    '''

    medication_list = list()

    def __init__(self, id, first_name,initial,paternal_last_name, maternal_last_name,image,birthday):

        '''
        Constructor to assign the needed variables
        '''
        self.id = id
        self.first_name = first_name
        self.initial = initial
        self.paternal_last_name = paternal_last_name
        self.maternal_last_name = maternal_last_name
        self.image = image
        self.birthday = birthday


    def get_full_name(self):
        '''
        Returns the full name of the Resident
        '''
        full_name = self.first_name

        if(self.initial != None):
            full_name += " "+self.initial

        full_name += " "+self.paternal_last_name

        if(self.maternal_last_name != None):
            full_name += " "+self.maternal_last_name

        return full_name
    
    def get_age(self):
        '''
        Calculates the correct age of the resident
        '''
        from datetime import date
        today = date.today()
        birthday = self.birthday

        age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
        if age <= 0:
            age = 0
        return age
    
    def get_image(self):
        '''
        Fetches the image to be displayed. If none was submitted then a default one will be provided
        '''
        image = self.image
        from .config.config import default_img
        if(image == None):
            image = default_img
        return image
        

        
    def set_medication_list(self, list):
        self.medication_list = list

    def get_medication_list(self):
        return self.medication_list




class Caretaker(UserMixin):
    '''
    Class for the Caretaker
    '''
    resident_list = list()

    def __init__(self, id, email, password,first_name,initial, paternal_last_name,maternal_last_name,phone_number,phone_provider,nursing_home_id):
        '''
        Constructor to assign the needed variables
        '''
        self.id = id
        self.first_name = first_name
        self.email = email
        self.password = password
        self.initial = initial
        self.paternal_last_name = paternal_last_name
        self.maternal_last_name = maternal_last_name
        self.phone_number = phone_number
        self.phone_provider = phone_provider
        self.nursing_home_id = nursing_home_id

    def get_full_name(self):
        '''
        Returns the full name of the Resident
        '''
        full_name = self.first_name

        if(self.initial != None):
            full_name += " "+self.initial

        full_name += " "+self.paternal_last_name

        if(self.maternal_last_name != None):
            full_name += " "+self.maternal_last_name

        return full_name
    
    def set_resident_list(self, list):
        self.resident_list = list

    def get_resident_list(self):
        return self.resident_list

class Nurse(UserMixin):
    '''
    Class for the Caretaker
    '''
    resident_list = list()

    def __init__(self,id,password,designation,image,first_name,initial,paternal_last_name,maternal_last_name, nursing_home_id):
        '''
        Constructor to assign the needed variables
        '''
        self.id = id
        self.password = password
        self.designation = designation
        self.image = image
        self.first_name = first_name        
        self.initial = initial
        self.paternal_last_name = paternal_last_name
        self.maternal_last_name = maternal_last_name
        self.nursing_home_id = nursing_home_id

    def get_full_name(self):
        '''
        Returns the full name of the Resident
        '''
        full_name = self.first_name

        if(self.initial != None):
            full_name += " "+self.initial

        full_name += " "+self.paternal_last_name

        if(self.maternal_last_name != None):
            full_name += " "+self.maternal_last_name

        return full_name
    
    def set_resident_list(self, list):
        self.resident_list = list

    def get_resident_list(self):
        return self.resident_list

class Medication:
    '''
    Class for the Medication
    '''
    pills_list = list()
    refill_list = list()

    def __init__(self, id, name, dosage, pill_quantity, pill_frequency, refill_quantity,start_date, perscription_date):
        '''
        Constructor to assign the needed variables
        '''
        self.id = id
        self.name = name
        self.dosage = dosage
        self.pill_quantity = pill_quantity
        self.pill_frequency = pill_frequency
        self.refill_quantity = refill_quantity
        self.start_date = start_date
        self.perscription_date = perscription_date
        

    def set_pill_list(self, list):
        self.pills_list = list
    
    def get_pill_list(self):
        return self.pills_list
    
    def set_refill_list(self, list):
        self.refill_list = list
    
    def get_refill_list(self):
        return self.refill_list  

    def get_perscription_daily_dose(self):
        return self.pill_frequency * self.dosage
    
    def get_estimated_end_date(self):
        from datetime import timedelta
        return self.start_date + timedelta(days=self.pill_quantity/self.pill_frequency)
    
class Pill:
    '''
    Class for each pill
    '''
    def __init__(self,id,taken_timestamp):
        '''
        Constructor to assign the needed variables
        '''
        self.id = id
        self.taken_timestamp = taken_timestamp

class Refill:
    '''
    Class for each refill
    '''
    def __init__(self,id,taken_timestamp):
        '''
        Constructor to assign the needed variables
        '''
        self.id = id
        self.taken_timestamp = taken_timestamp