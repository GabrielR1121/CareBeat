class Caree:
    '''
    Class for the Caree
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
        Returns the full name of the Caree
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




class Caretaker:
    '''
    Class for the Caretaker
    '''
    def __init__(self, id):
        '''
        Constructor to assign the needed variables
        '''
        self.id = id


class Medication:
    '''
    Class for the Medication
    '''
    def __init__(self, id, name, dosage, pill_quantity, pill_frequency, start_date, perscription_date):
        '''
        Constructor to assign the needed variables
        TODO: create methods for prescription daily dose, estimated end date
        '''
        self.id = id
        self.name = name
        self.dosage = dosage
        self.pill_quantity = pill_quantity
        self.pill_frequency = pill_frequency
        self.start_date = start_date
        self.perscription_date = perscription_date
    
    def get_encrypted_id(self):
        return self.encryptor.get_encrypted_id(self.id)

    def get_decrypted_id(self, encrypted_number):
        return self.encryptor.get_decrypted_id(encrypted_number)

    def get_perscription_daily_dose(self):
        return self.pill_frequency * self.dosage
    
    def get_estimated_end_date(self):
        from datetime import timedelta
        return self.start_date + timedelta(days=self.pill_quantity/self.pill_frequency)