from flask_login import UserMixin
from datetime import datetime,timedelta
from scipy.stats import linregress
import numpy as np
from fuzzywuzzy import fuzz
from decimal import Decimal
from datetime import date

class Resident:
    '''
    Class for the Resident
    '''
    
    vitals_list = []
    temp_check = weight_check= systolic_bp_check = diastolic_bp_check = heart_rate_check = glucose_check = False

    min_temp = 95
    max_temp = 100.4

    min_systolic_bp = 90
    max_systolic_bp = 121

    min_diastolic_bp = 61
    max_diastolic_bp = 80

    min_heart_rate = 60
    max_heart_rate = 100

    min_glucose = 94
    max_glucose = 140

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
    
    def get_active_flags(self):
        """
        Searches the min and max of each vital in order to find if the residnet information is within in normal ranges or not.
        Returns a list of active flags with the condition names
        """
        active_flags  = []
        if len(self.vitals_list) >=1:

            if self.get_baseline([int(vital.temperature) for vital in self.vitals_list]) < self.min_temp or self.get_baseline([int(vital.temperature) for vital in self.vitals_list]) > self.max_temp:
                active_flags.append("Temp")

            if self.get_baseline([vital.systolic_blood_pressure for vital in self.vitals_list]) < self.min_systolic_bp or self.get_baseline([vital.diastolic_blood_pressure for vital in self.vitals_list]) > self.max_systolic_bp:
                active_flags.append("Blood Pressure")
            
            if self.get_baseline([vital.heart_rate for vital in self.vitals_list]) < self.min_heart_rate or self.get_baseline([vital.heart_rate for vital in self.vitals_list]) > self.max_heart_rate:

                active_flags.append("Heart Rate")

            if self.get_baseline([int(vital.glucose) for vital in self.vitals_list]) < self.min_glucose or self.get_baseline([int(vital.glucose) for vital in self.vitals_list]) > self.max_glucose:

                active_flags.append("Glucose")
            
        return active_flags

    def check_blood_pressure(self):
        """
        Checks in which category the blood pressure is in
        """
        systolic_bp = self.get_baseline([vital.systolic_blood_pressure for vital in self.vitals_list])
        diastolic_bp = self.get_baseline([vital.diastolic_blood_pressure for vital in self.vitals_list])

        condition = ""
        if 70 <= systolic_bp <= 90 and 40 <= diastolic_bp <= 60:
            condition = "Low Blood Pressure"
        elif 90 <= systolic_bp <= 120 and 60 <= diastolic_bp <= 80:
            condition = "Normal Blood Pressure"
        elif 120 <= systolic_bp <= 140 and 80 <= diastolic_bp <= 90:
            condition = "Pre-Hypertension"
        elif 140 <= systolic_bp <= 160 and 90 <= diastolic_bp <= 100:
            condition = "High: Stage 1 Hypertension"
        elif systolic_bp > 160 or diastolic_bp > 100:
            condition = "High: Stage 2 Hypertension"

        
        return condition
    
    def check_glucose(self):
        """
        Checks what categort the glucose is in
        """
        glucose = self.get_baseline([int(vital.glucose) for vital in self.vitals_list])

        condition = ""
        if 99 <= glucose <= 140:
            condition = 'Normal'
        elif 140 <= glucose <= 160:
            condition = 'Imparied Glucose'
        else:
            condition = 'Diabetic'

        
        return condition
    
    def check_heart_rate(self):
        """
        Checks what category the heart rate is 
        """
        pulse = self.get_baseline([int(vital.heart_rate) for vital in self.vitals_list])
        if pulse <= 59:
            return "Low"
        elif 60 <= pulse < 100:
            return "Normal"
        elif 100 <= pulse < 120:
            return "Mild Tachycardia"
        elif 120 <= pulse < 150:
            return 'Moderate Tachycardia'
        else:
            return "Severe Tachycardia"
        
    def check_temp(self):
        """
        Checks in what category the temperature is
        """
        temp = self.get_baseline([int(vital.temperature) for vital in self.vitals_list])

        if temp <95:
            return "Hypothermia"
        elif 95 <= temp < 100.4:
            return "Normal"
        elif 100.4 <= temp < 104.0:
            return "Fever"
        else:
            return "Hyperthermia"

    def check_condition(self,medication_list,vital):
        """
        Analyzes the vitals data seeing if there are anamolies in the data and returns the result
        """
        # Check if vital has less than 2 items
        if len(vital) < 2:
            return 0
        timestamps = [time.timestamp for time in self.vitals_list]

        filtered_data = {
            timestamp: vital_value
            for timestamp, vital_value in zip(timestamps, vital)
        }

        # Filter data for the current month
        current_month = datetime.now().strftime('%Y-%m')
        
        timestamps = list(filtered_data.keys())
        # Create a new list of medications with start dates approximately matching the timestamps
        matching_medication = [medication for medication in medication_list if medication.start_date.strftime('%Y-%m') == current_month]

        # Calculate baseline for vital data
        slope, intercept, _, _, _ = linregress(range(len(vital)), vital)
        baseline_vital = np.array([slope * i + intercept for i in range(len(vital))])

        # Calculate standard deviation of vital
        std_dev_vital = np.std(vital)
        # Calculate the threshold for vital outliers dynamically
        outlier_threshold_vital = 2 * std_dev_vital  

        # Identify vital BP outliers
        outliers_vital = np.where(abs(vital - baseline_vital) > outlier_threshold_vital)[0]

        # Remove vital BP outliers for linear regression calculation
        filtered_vital_bp = np.delete(vital, outliers_vital)

        # Calculate baseline for vital data without outliers
        slope, intercept, _, _, _ = linregress(range(len(filtered_vital_bp)), filtered_vital_bp)
        baseline_vital = np.array([slope * i + intercept for i in range(len(vital))])

        spike_data = []
        all_data = []
        flag = False
        if len(outliers_vital) > 0:
            spikes = np.sort(np.arange(min(outliers_vital)-1, min(outliers_vital)-3, -1))
            all_data = np.insert(outliers_vital, 0, spikes, axis=0)
            spike_data = [vital[i] for i in all_data]
            flag = True

        return [flag, spike_data, outliers_vital, range(len(vital)), baseline_vital, all_data, matching_medication, vital,timestamps]

    
    def get_baseline(self,vital):
        """
        Analyzes the vitals data seeing if there are anamolies in the data and returns the result
        """
        # Check if vital has less than 2 items
        if len(vital) < 2:
            return 0
        timestamps = [time.timestamp for time in self.vitals_list]


        filtered_data = {
            timestamp: vital
            for timestamp, vital in zip(timestamps, vital)
        }
        timestamps = list(filtered_data.keys())
         # Calculate baseline for vital data
        slope, intercept, _, _, _ = linregress(range(len(vital)), vital)
        baseline_vital = np.array([slope * i + intercept for i in range(len(vital))])

        # Calculate standard deviation of vital
        std_dev_vital = np.std(vital)
        # Calculate the threshold for vital outliers dynamically
        outlier_threshold_vital = 2 * std_dev_vital  

        # Identify vital BP outliers
        outliers_vital = np.where(abs(vital - baseline_vital) > outlier_threshold_vital)[0]
        
        # Remove vital BP outliers for linear regression calculation
        filtered_vital = np.delete(vital, outliers_vital)

        # Calculate baseline for vital data without outliers
        slope, intercept, _, _, _ = linregress(range(len(filtered_vital)), filtered_vital)
        baseline_vital = np.array([slope * i + intercept for i in range(len(vital))])
        return round(sum(baseline_vital)/len(baseline_vital))
    
    #Associates a medicaiton with a specific condition
    def medication_condition(self,type,med_list):
        #Determines the condition in order to search accordingly
        if type == 'Blood Pressure':
            conditions = ["Low Blood Pressure", "Pre-Hypertension", "High: Stage 1 Hypertension", "High: Stage 2 Hypertension"]
        elif type == 'Glucose':
            conditions = ["Diabetes"]
        elif type == 'Pulse':
            conditions = ["Tachycardia"]
        else:
            conditions = ["Temperature"]

        
        filtered_medications = []
        
        for medication in med_list:
            diagnosis_list = medication.get_diagnosis_list()
            
            for diagnosis in diagnosis_list:
                
                # Use fuzzy matching to compare diagnosis to BP conditions
                for vital in conditions:
                    similarity_ratio = fuzz.ratio(diagnosis.name.lower(), vital.lower())
                    
                    # Adjust the threshold based on your preference
                    if similarity_ratio > 70:  # You can adjust this threshold
                        filtered_medications.append(medication)
                        break  # Break out of the loop if a match is found
        return filtered_medications

    #Assess if patient requires periodic wellness checks
    def conduct_periodic_wellness_checks(self):
        timestamp_list = []

        # Assuming self.vitals_list contains objects of type Vital with a 'timestamp' attribute
        for vital_obj in self.vitals_list:
            timestamp_list.append(vital_obj.timestamp)

        # Get the current date
        current_date = datetime.now().date()

        # Filter timestamps for the current day
        current_day_timestamps = [timestamp for timestamp in timestamp_list if timestamp.date() == current_date]

        daily_checks_left = 2 - len(current_day_timestamps)

        if daily_checks_left <= 0:
            daily_checks_left = 0
        return daily_checks_left

    #Stores the list of vitals objects
    def set_vitals_list(self, list):
        self.vitals_list = list

    #Gets the list of vital objects
    def get_vitals_list(self):
        return self.vitals_list
    
    #Get the monthly vitals
    def get_month_vitals(self):
        # Filter data for the current month
        current_month = datetime.now().strftime('%Y-%m')
        filtered_data = {
            vital.timestamp: vital
            for vital in self.vitals_list
            if vital.timestamp.strftime('%Y-%m') == current_month
        }
        return filtered_data
    
    #Stores the list of medication objects
    def set_medication_list(self, list):
        self.medication_list = list

    #Add any medication to the medication list
    def add_medication(self, medication):
        self.medication_list.append(medication)

    #Gets the list of medication objects
    def get_medication_list(self):
        return self.medication_list
    
    #Calculates the A1C of the resident
    def calculate_A1C(self):
        glucose_list = []
        for vital in self.vitals_list:
            glucose_list.append(vital.glucose)
        average_glucose = sum(glucose_list) / len(glucose_list)

        # Convert average_glucose to Decimal before performing the operation
        average_glucose_decimal = Decimal(str(average_glucose))
        
        # Use Decimal constants to ensure both operands are Decimal
        result = (average_glucose_decimal + Decimal('46.7')) / Decimal('28.7')
        
        return round(result,1)

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
    diagnosis_list = list()

    morning_bool = str()
    noon_bool = str()
    evening_bool = str()
    bedtime_bool = str()
    refill_bool = False
    priority = int()

    def __init__(self, id, name, dosage, pill_quantity, pill_frequency, refill_quantity,start_date, perscription_date,half_life):
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
        self.half_life = half_life

    def calculate_priority(self, emergency_admin):
        """
        Sets the priority of the medication
        """
        #Time until next dose
        time_until_next_dose = self.time_until_next_dose().total_seconds() / 3600  # convert to hours

        # Define priority levels
        CRITICAL_PRIORITY = 0
        HIGH_PRIORITY = 1
        MEDIUM_PRIORITY = 2
        LOW_PRIORITY = 3
        NO_PRIORITY = 4

        # Set priority based on criteria
        if time_until_next_dose <= 2:  # If the next dose is within 2 hours, consider high priority
            self.priority = HIGH_PRIORITY
        elif 2 < time_until_next_dose <= 8:  # If the next dose is within 8 hours, consider medium priority
            self.priority = MEDIUM_PRIORITY
        else:
            self.priority = LOW_PRIORITY

        for medication in emergency_admin:
            if self.name == medication.name:
                self.priority = CRITICAL_PRIORITY
        
        if (self.refill_quantity - self.amount_refill()) > 0 and self.medication_taken() <= self.pill_quantity*0.2:
            self.priority = CRITICAL_PRIORITY
        elif self.refills_left() == 0 and (self.medication_taken() ==0):
            self.priority = NO_PRIORITY

    def get_last_taken(self):
        """
        Gets the last pill taken timestamp or the start date
        """
        if self.pills_list:
            return self.pills_list[-1].taken_timestamp
        else:
            return self.start_date
    
    def get_time_frequency(self):
        """
        Calculates the time span of when the next pill should be taken
        """
        return 24/self.pill_frequency
    
    def next_dose(self):
        """
        Calculates the next dose
        """
        return self.get_last_taken() + timedelta(hours=self.get_time_frequency())
    
    def time_until_next_dose(self):
        """
        Calculates the time it takes for the next dose
        """
        current_time = datetime.now()
        time_until_next_dose = self.next_dose() - current_time
        return time_until_next_dose

    def get_string_time(self):
        time = self.time_until_next_dose()

        if time:
            total_seconds = int(time.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            formatted_time = "{:02}:{:02}:{:02}".format(hours, minutes, seconds)
        else:
            formatted_time = 'N/A'

        return formatted_time
    

    def when_taken(self):
        """
        Caluclates when the medications are taken with consistency each day
        """
        import datetime
        #Set Start and End time for the morning between 6 am and 11 am
        morning_start = datetime.time(6, 0)
        morning_end = datetime.time(11, 0)
        #Set Start and End Time for noon between 11 am and 2 pm
        noon_start = datetime.time(11, 0)
        noon_end = datetime.time(14, 0)
        #Set Start and End Time for evening between 2 pm and 8 pm
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
        consistency_threshold = 0.5 

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

    #Sets the pill list objects
    def set_pill_list(self, list):
        self.pills_list = list
        self.when_taken()
    
    #Gets the pill list objects
    def get_pill_list(self):
        return self.pills_list
    
    #Sets the diagnosis list objects
    def set_diagnosis_list(self, list):
        self.diagnosis_list = list
    
    #Gets the diagnosis list objects 
    def get_diagnosis_list(self):
        return self.diagnosis_list
    
    #Sets the refill list objects 
    def set_refill_list(self, list):
        self.refill_list = list
    
    #Gets the refill list objects
    def get_refill_list(self):
        return self.refill_list  

    #Gets the perscription daily dose
    def get_perscription_daily_dose(self):
        return self.pill_frequency * self.dosage
    
    #Gets the estimates end date of the medication
    def get_estimated_end_date(self):
        from datetime import timedelta
        estimate = self.start_date + timedelta(days=self.pill_quantity/self.pill_frequency)
        return estimate
    
    #Gets the start date of the medcation
    def get_start_date(self):
        import calendar
        return "{0}-{1}-{2}".format(self.start_date.day,calendar.month_abbr[self.start_date.month],self.start_date.year)
    
    #Gets the amount of refills the medication has
    def amount_refill(self):
        count = 0
        for _ in self.refill_list:
            count+=1

        return count
    
    #Gets how many pill have been taken up until now
    def medication_taken(self):
        total=0
        rem = 0
        z = len(self.refill_list) * self.pill_quantity

        for _ in self.pills_list:
            total +=1
            if z > 0 and len(self.refill_list) <= self.refill_quantity:
                rem = (self.pill_quantity - total) + self.pill_quantity


        z = len(self.refill_list) * self.pill_quantity
       
        if z == 0:
            rem = self.pill_quantity - total
        return rem
    
    #Gets how many refills the medicaiton has left
    def refills_left(self):
        Refills_left = self.refill_quantity-len(self.refill_list)
        if Refills_left > 0 and self.pill_quantity-self.medication_taken() <= self.pill_quantity*0.2:
            return self.pill_quantity
        else:
            return 0

    #Gets the total availble amount of pills
    def total_available_pills(self):
       return (self.pill_quantity - self.medication_taken()) + self.refills_left()



class Diagnosis:
    '''
    Class for Diagnosis
    '''

    def __init__(self,id,name):
        self.id = id
        self.name = name
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
    Class for Refill
    '''
    def __init__(self,id,taken_timestamp):
        '''
        Constructor to assign the needed variables
        '''
        self.id = id
        self.taken_timestamp = taken_timestamp


class Wellness_check:
    '''
    Class for each Wellness Check
    '''
    def __init__(self, id=None, timestamp=None, rating=None, description=None):
        self.id = id
        self.timestamp = timestamp if timestamp is not None else datetime.now()
        self.rating = rating
        self.description = description



class Vitals:
    '''
    Class for Vital Check
    '''
    def __init__(self, id=None, timestamp=None, temperature=None, weight=None, systolic_blood_pressure=None, diastolic_blood_pressure=None, heart_rate=None, glucose=None):
        self.id = id
        self.timestamp = timestamp if timestamp is not None else datetime.now()
        self.temperature = temperature if temperature != '' else None
        self.weight = weight if weight != '' else None
        self.systolic_blood_pressure = systolic_blood_pressure if systolic_blood_pressure != '' else None
        self.diastolic_blood_pressure = diastolic_blood_pressure if diastolic_blood_pressure != '' else None
        self.heart_rate = heart_rate if heart_rate != '' else None
        self.glucose = glucose if glucose != '' else None