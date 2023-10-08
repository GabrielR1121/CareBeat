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

    def __init__(self,role,id, email, password,first_name,initial, paternal_last_name,maternal_last_name,phone_number,phone_provider,nursing_home_id):
        '''
        Constructor to assign the needed variables
        '''
        self.role = role
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
    Class for the Nurse
    '''
    resident_list = list()

    def __init__(self,role,id,password,designation,image,first_name,initial,paternal_last_name,maternal_last_name, nursing_home_id):
        '''
        Constructor to assign the needed variables
        '''
        self.role = role
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
    morning_bool = str()
    noon_bool = str()
    evening_bool = str()
    bedtime_bool = str()

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
        

    def when_taken(self):
        import datetime
        morning_start = datetime.time(6, 0)
        morning_end = datetime.time(11, 0)

        noon_start = datetime.time(11, 0)
        noon_end = datetime.time(14, 0)

        evening_start = datetime.time(14, 0)
        evening_end = datetime.time(20, 0)

        # Initialize variables to count medication usage
        morning_count = 0
        noon_count = 0
        evening_count = 0
        bedtime_count = 0

        pill_list = self.get_pill_list()

        for pill in pill_list:
            time_taken = pill.taken_timestamp.time()
            if morning_start <= time_taken < morning_end:
                morning_count += 1
            elif noon_start <= time_taken < noon_end:
                noon_count += 1
            elif evening_start <= time_taken < evening_end:
                evening_count += 1
            else:
                bedtime_count += 1

        # Define consistency threshold
        consistency_threshold = 0.1 

        # Calculate percentages with error handling
        try:
            morning_percentage = morning_count / len(pill_list)
        except ZeroDivisionError:
            morning_percentage = 0

        try:
            noon_percentage = noon_count / len(pill_list)
        except ZeroDivisionError:
            noon_percentage = 0

        try:
            evening_percentage = evening_count / len(pill_list)
        except ZeroDivisionError:
            evening_percentage = 0

        try:
            bedtime_percentage = bedtime_count / len(pill_list)
        except ZeroDivisionError:
            bedtime_percentage = 0

        # Set variables to "X" based on consistency
        self.morning_bool = "X" if morning_percentage >= consistency_threshold else ""
        self.noon_bool = "X" if noon_percentage >= consistency_threshold else ""
        self.evening_bool = "X" if evening_percentage >= consistency_threshold else ""
        self.bedtime_bool = "X" if bedtime_percentage >= consistency_threshold else ""

        #print(f"{self.name}")
        #print(f"For Morning Percentage: {morning_percentage}")
        #print(f"Noon Percentage: {noon_percentage}")
        #print(f"Evening Percentage: {evening_percentage}")
        #print(f"Bedtime Percentage: {bedtime_percentage}")




    def set_pill_list(self, list):
        self.pills_list = list
        self.when_taken()
    
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
        estimate = self.start_date + timedelta(days=self.pill_quantity/self.pill_frequency)
        return estimate
    
    def get_start_date(self):
        import calendar
        return "{0}-{1}-{2}".format(self.start_date.day,calendar.month_abbr[self.start_date.month],self.start_date.year)
    
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