from .config import db_config
import mysql.connector
from mysql.connector import Error
import calendar
from website.models import Resident, Caretaker, Medication, Pill, Refill, Nurse,Wellness_check, Vitals,Diagnosis
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta


def connect_to_db():
    """
    Connect to database using credentials in another file to sign in
    """
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print("The Database could not connect. ", e)


def get_graph1_data(medication, resident):
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(
        """
                    SELECT DATE(taken_timestamp), COUNT(*)
                    FROM PILL
                    INNER JOIN PHARMACEUTICAL ON PILL.PHARMACEUTICAL_fk = PHARMACEUTICAL.id_pk
                    INNER JOIN MEDICATION ON PHARMACEUTICAL.MEDICATION_pk_fk = MEDICATION.id_pk
                    INNER JOIN RESIDENT ON PHARMACEUTICAL.RESIDENT_pk_fk = RESIDENT.id_pk
                    WHERE MEDICATION.id_pk = {0} AND RESIDENT.id_pk = {1}
                    GROUP BY DATE(taken_timestamp)
                   """.format(medication.id, resident.id))
    data = cursor.fetchall()
    if len(data) != 0:
        date_ls = [date for date, _ in data]
        date_ls.insert(0, date_ls[0] - timedelta(1))
        # Find the min and max dates in date_ls
        min_date = min(date_ls)
        max_date = max(date_ls)
        # Create a list of date objects within the specified range
        date_range = [min_date + timedelta(days=i) for i in range((max_date - min_date).days + 1)]
        # Initialize the result list with zeros
        amount_ls = [0] * len(date_range)
        # Fill in the daily_avg list with correct values from data
        for date, amount in data:
            # Ensure the date object is in the same format as date_range
            if date in date_ls:
                index = (date - min_date).days  # Calculate the index based on the difference between the date and min_date
                amount_ls[index] = amount
    else:
        date_ls = []
        amount_ls = []
        date_range = []

    cursor.close()
    connection.close()

    return {"Date": date_range, "Amount": amount_ls}


def get_graph2_data(medication, resident):
    """
    Gets data for second chart
    """
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(
        """
                    SELECT COUNT(*)
                    FROM PILL
                    INNER JOIN PHARMACEUTICAL ON PILL.PHARMACEUTICAL_fk = PHARMACEUTICAL.id_pk
                    INNER JOIN MEDICATION ON PHARMACEUTICAL.MEDICATION_pk_fk = MEDICATION.id_pk
                    INNER JOIN RESIDENT ON PHARMACEUTICAL.RESIDENT_pk_fk = RESIDENT.id_pk
                    WHERE MEDICATION.id_pk = {0} AND RESIDENT.id_pk = {1}
                    GROUP BY MEDICATION.name
                   """.format(medication.id, resident.id))
    data = cursor.fetchone()
    if data:
        amount = data[0]
    else:
        amount = 0

    med_name = medication.name
    total_pills = medication.pill_quantity

    cursor.close()
    connection.close()

    return (med_name, amount, total_pills)


def get_graph3_data(medication, resident):
    connection = connect_to_db()
    cursor = connection.cursor()

    cursor.execute(
        """
                SELECT EXTRACT(MONTH FROM taken_timestamp) as mon,count(*)
                FROM PILL
                INNER JOIN PHARMACEUTICAL ON PILL.PHARMACEUTICAL_fk = PHARMACEUTICAL.id_pk
                INNER JOIN MEDICATION ON PHARMACEUTICAL.MEDICATION_pk_fk = MEDICATION.id_pk
                INNER JOIN RESIDENT ON PHARMACEUTICAL.RESIDENT_pk_fk = RESIDENT.id_pk
                WHERE MEDICATION.id_pk = {0} AND RESIDENT.id_pk = {1}
                GROUP BY EXTRACT(MONTH FROM taken_timestamp)
                ORDER BY mon
                   """.format(medication.id, resident.id))

    data = cursor.fetchall()
    if len(data) != 0:
        date_ls, amount_ls = zip(*[(str(calendar.month_name[month_num]), amount)for month_num, amount in data])
    else:
        date_ls = []
        amount_ls = []

    cursor.close()
    connection.close()

    return {"Date": date_ls, "Amount": amount_ls}


def get_graph4_data(medication, resident):
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(
        """
                SELECT DATE(taken_timestamp), COUNT(*), PHARMACEUTICAL.PILL_frequency
                FROM PILL
                INNER JOIN PHARMACEUTICAL ON PILL.PHARMACEUTICAL_fk = PHARMACEUTICAL.id_pk
                INNER JOIN MEDICATION ON PHARMACEUTICAL.MEDICATION_pk_fk = MEDICATION.id_pk
                INNER JOIN RESIDENT ON PHARMACEUTICAL.RESIDENT_pk_fk = RESIDENT.id_pk
                WHERE MEDICATION.id_pk = {0} AND RESIDENT.id_pk = {1}
                GROUP BY DATE(taken_timestamp), PHARMACEUTICAL.PILL_frequency
                   """.format(medication.id, resident.id))
    data = cursor.fetchall()
    if len(data) != 0:
        date_ls = [date for date, _, _ in data]
        date_ls.insert(0, date_ls[0] - timedelta(1))

        # Find the min and max dates in date_ls
        min_date = min(date_ls)
        max_date = max(date_ls)

        # Create a list of date objects within the specified range
        date_range = [min_date + timedelta(days=i) for i in range((max_date - min_date).days + 1)]

        # Initialize the result list with zeros
        daily_avg = [0] * len(date_range)

        # Fill in the daily_avg list with correct values from data
        for date, amount, total in data:
            # Ensure the date object is in the same format as date_range
            if date in date_ls:
                index = (date - min_date).days  # Calculate the index based on the difference between the date and min_date
                daily_avg[index] = (amount / total) * 100
    else:
        date_ls = []
        daily_avg = []
        date_range = []

    cursor.close()
    connection.close()
    return {"Date": date_range, "Average": daily_avg}


def get_graph5_data(medication, resident):
    data = get_graph4_data(medication, resident)

    date_range = data["Date"][1:]
    daily_avg = data["Average"][1:]
    weeks = list()
    weekly_avg = list()

    for index, date in enumerate(date_range):
        if index % 7 == 0:
            weeks.append(date)

    for i in range(0, len(daily_avg), 7):
        new_list = daily_avg[i : i + 7]
        weekly_avg.append(sum(new_list) / len(new_list))

    if weeks:
        weeks.insert(0, weeks[0] - timedelta(7))
    else:
        weeks = []

    if weekly_avg:
        weekly_avg.insert(0, 0)
    else:
        weekly_avg = []

    return {"Week": weeks, "Average": weekly_avg}


def get_graph6_data(medication, resident):
    """
    Gets data for sixth chart
    """
    from collections import defaultdict

    data = get_graph5_data(medication, resident)
    date_range = data["Week"][1:]
    weekly_avg = data["Average"][1:]

    if len(data) != 0 and date_range and weekly_avg:
        # Create a dictionary to store the monthly sums and counts
        monthly_data = defaultdict(lambda: {"sum": 0, "count": 0})

        # Extract the first date from date_range
        first_date = date_range[0]

        # Subtract 1 month from the first date
        previous_month_date = first_date - relativedelta(months=1)

        previous_month_name = calendar.month_name[previous_month_date.month]

        # Add the previous month's data to the monthly_data dictionary
        monthly_data[previous_month_name] = {"sum": 0, "count": 1}

        # Iterate through date_range and weekly_avg
        for date, weekly_amnt in zip(date_range, weekly_avg):
            # Add the monthly sum and increase the count
            month_name = calendar.month_name[date.month]
            monthly_data[month_name]["sum"] += weekly_amnt
            monthly_data[month_name]["count"] += 1

        # Calculate the monthly averages
        monthly_avg = {}
        for month_name, data in monthly_data.items():
            monthly_avg[month_name] = data["sum"] / data["count"]
    else:
        monthly_avg = {}
        monthly_avg[calendar.month_name[datetime.now().month]] = 0

    return {"Date": list(monthly_avg.keys()), "Average": list(monthly_avg.values())}


def get_graph7_data(medication, resident):
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(
        """
                SELECT COUNT(*)
                FROM PILL
                INNER JOIN PHARMACEUTICAL ON PILL.PHARMACEUTICAL_fk = PHARMACEUTICAL.id_pk
                INNER JOIN MEDICATION ON PHARMACEUTICAL.MEDICATION_pk_fk = MEDICATION.id_pk
                INNER JOIN RESIDENT ON PHARMACEUTICAL.RESIDENT_pk_fk = RESIDENT.id_pk
                WHERE MEDICATION.id_pk = {0} AND RESIDENT.id_pk = {1}
                GROUP BY MEDICATION.name
                   """.format(medication.id, resident.id))
    data = cursor.fetchone()
    if data:
        amount = data[0]
    else:
        amount = 0
    med_name = medication.name
    total_pills = medication.pill_quantity
    cursor.close()
    connection.close()

    return (med_name, amount, total_pills)


def get_graph8_data(medication, resident):
    connection = connect_to_db()
    cursor = connection.cursor()

    cursor.execute(
        """
                SELECT DATE(PILL.taken_timestamp), PHARMACEUTICAL.dose, COUNT(*)
                FROM PILL
                INNER JOIN PHARMACEUTICAL ON PILL.PHARMACEUTICAL_fk = PHARMACEUTICAL.id_pk
                INNER JOIN MEDICATION ON PHARMACEUTICAL.MEDICATION_pk_fk = MEDICATION.id_pk
                INNER JOIN RESIDENT ON PHARMACEUTICAL.RESIDENT_pk_fk = RESIDENT.id_pk
                WHERE MEDICATION.id_pk = {0} AND RESIDENT.id_pk = {1}
                GROUP BY DATE(taken_timestamp), PHARMACEUTICAL.dose, PHARMACEUTICAL.PILL_frequency;
                   """.format(medication.id, resident.id))
    data = cursor.fetchall()
    if len(data) != 0:
        date_ls = [date for date, _, _ in data]
        date_ls.insert(0, date_ls[0] - timedelta(1))
        # Find the min and max dates in date_ls
        min_date = min(date_ls)
        max_date = max(date_ls)
        # Create a list of date objects within the specified range
        date_range = [min_date + timedelta(days=i) for i in range((max_date - min_date).days + 1)]
        daily_dose_ls = [0] * len(date_range)
        daily_dose_avg_ls = list()
        for date, dose, amount in data:
            if date in date_ls:
                index = (date - min_date).days
                daily_dose_ls[index] = dose * amount
        for index in range(1, len(daily_dose_ls) + 1):
            daily_dose_avg_ls.append(
                sum(daily_dose_ls[:index]) / len(daily_dose_ls[:index]))
    else:
        date_range = []
        date_ls = []
        daily_dose_avg_ls = []
    cursor.close()
    connection.close()
    return {"Date": date_range, "Dose (mg)": daily_dose_avg_ls}


def get_graph9_data(medication, resident):
    return get_graph1_data(medication, resident)


def get_graph10_data(medication, resident):
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(
        """
                SELECT PILL.taken_timestamp
                FROM PILL
                INNER JOIN PHARMACEUTICAL ON PILL.PHARMACEUTICAL_fk = PHARMACEUTICAL.id_pk
                INNER JOIN MEDICATION ON PHARMACEUTICAL.MEDICATION_pk_fk = MEDICATION.id_pk
                INNER JOIN RESIDENT ON PHARMACEUTICAL.RESIDENT_pk_fk = RESIDENT.id_pk
                WHERE MEDICATION.id_pk = {0} AND RESIDENT.id_pk = {1}
                GROUP BY PILL.taken_timestamp;
                   """.format(
            medication.id, resident.id
        )
    )

    data = cursor.fetchall()

    if data:
        datetime_ls = [dateTime[0] for dateTime in data]
    else:
        datetime_ls = []

    cursor.close()
    connection.close()

    return {"DateTime": datetime_ls, "Dose": medication.dosage}


def verify_login(email=None, id=None):
    connection = connect_to_db()
    cursor = connection.cursor()
    if email:
        cursor.execute(
            """
                SELECT DISTINCT
				'Caretaker' as Role,
                C.id_pk AS caretaker_id,
                C.email,
                C.password,
                C.first_name,
                C.initial,
                C.paternal_last_name,
                C.maternal_last_name,
                C.phone_number,
                C.phone_provider,
                R.nursing_home_fk AS nursing_home_id
                FROM CARETAKER C
                LEFT JOIN RESIDENT R ON C.id_pk = R.caretaker_fk
                LEFT JOIN NURSING_HOME NH ON R.nursing_home_fk = NH.id_pk
                WHERE C.email = %s; 
                   """,
            (email,),
        )
    else:
        cursor.execute(
            """
                SELECT 'Nurse' as Role, id_pk,password,designation,image,first_name,intial, paternal_last_name,maternal_last_name,nursing_home_fk
                FROM NURSE
                WHERE id_pk = %s
                   """,
            (id,),
        )
    if email:
        for (role,id,email,password,first_name,initial,paternal_last_name,maternal_last_name,phone_number,phone_provider,nursing_home_id,) in cursor.fetchall():
            caretaker = Caretaker(role,id,email,password,first_name,initial,paternal_last_name,maternal_last_name,phone_number,phone_provider,nursing_home_id)
            caretaker.set_resident_list(get_residents(caretaker))
            return caretaker
    else:
        for (role,id,password,designation,image,first_name,initial,paternal_last_name,maternal_last_name,nursing_home_id) in cursor.fetchall():
            nurse = Nurse(role,id,password,designation,image,first_name,initial,paternal_last_name,maternal_last_name,nursing_home_id)
            nurse.set_resident_list(get_residents(nurse))
            return nurse


def get_nurse(id):
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(
        """
                SELECT 'Nurse' as Role, id_pk,password,designation,image,first_name,intial, paternal_last_name,maternal_last_name,nursing_home_fk
                FROM NURSE
                WHERE id_pk = %s
                   """,
        (id,),
    )

    for (role,id,password,designation,image,first_name,initial,paternal_last_name,maternal_last_name,nursing_home_id,) in cursor.fetchall():
        nurse = Nurse(role,id,password,designation,image,first_name,initial,paternal_last_name,maternal_last_name,nursing_home_id,)
        nurse.set_resident_list(get_residents(nurse))
        return nurse


def get_caretaker(id):
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(
        """
                SELECT DISTINCT
                'Caretaker' as Role,
                C.id_pk AS caretaker_id,
                C.email,
                C.password,
                C.first_name,
                C.initial,
                C.paternal_last_name,
                C.maternal_last_name,
                C.phone_number,
                C.phone_provider,
                R.nursing_home_fk AS nursing_home_id
                FROM CARETAKER C
                LEFT JOIN RESIDENT R ON C.id_pk = R.caretaker_fk
                LEFT JOIN NURSING_HOME NH ON R.nursing_home_fk = NH.id_pk
                WHERE C.id_pk = %s; 
                   """,
        (id,),
    )

    for (role,id,email,password,first_name,initial,paternal_last_name,maternal_last_name,phone_number,phone_provider,nursing_home_id,) in cursor.fetchall():
        caretaker = Caretaker(role,id,email,password,first_name,initial,paternal_last_name,maternal_last_name,phone_number,phone_provider,nursing_home_id)
        caretaker.set_resident_list(get_residents(caretaker))
        return caretaker


def get_caretaker_resident(resident):
    connection = connect_to_db()
    cursor = connection.cursor()

    cursor.execute("""
SELECT DISTINCT
                'Caretaker' as Role,
                C.id_pk AS caretaker_id,
                C.email,
                C.password,
                C.first_name,
                C.initial,
                C.paternal_last_name,
                C.maternal_last_name,
                C.phone_number,
                C.phone_provider,
                R.nursing_home_fk AS nursing_home_id
                FROM CARETAKER C
                LEFT JOIN RESIDENT R ON C.id_pk = R.caretaker_fk
                LEFT JOIN NURSING_HOME NH ON R.nursing_home_fk = NH.id_pk
                WHERE R.id_pk = {0}; 
                   """.format(resident.id))
    for (role,id,email,password,first_name,initial,paternal_last_name,maternal_last_name,phone_number,phone_provider,nursing_home_id,) in cursor.fetchall():
        return Caretaker(role,id,email,password,first_name,initial,paternal_last_name,maternal_last_name,phone_number,phone_provider,nursing_home_id)
        


def get_pill_taken(medication, resident):
    """
    Gets the amount of pills taken
    """
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(
        """
                    SELECT COUNT(*)
                    FROM PILL
                    INNER JOIN PHARMACEUTICAL ON PILL.PHARMACEUTICAL_fk = PHARMACEUTICAL.id_pk
                    INNER JOIN MEDICATION ON PHARMACEUTICAL.MEDICATION_pk_fk = MEDICATION.id_pk
                    INNER JOIN RESIDENT ON PHARMACEUTICAL.RESIDENT_pk_fk = RESIDENT.id_pk
                    WHERE MEDICATION.id_pk = {0} AND RESIDENT.id_pk = {1}
                   """.format(
            medication.id, resident.id
        )
    )

    pill_taken = cursor.fetchone()[0]

    return pill_taken


def get_residents(user):
    """
    Gets a list of residents
    """
    connection = connect_to_db()
    cursor = connection.cursor()

    if user.role == 'Caretaker':
        cursor.execute(
            """
        SELECT *
        FROM RESIDENT
        WHERE 
        (RESIDENT.caretaker_fk = %s OR %s IS NULL)
        AND RESIDENT.nursing_home_fk = %s;
        """,
            (
                user.id,
                user.id,
                user.nursing_home_id,
            ),
        )
    else:
        cursor.execute(
            """
        SELECT *
        FROM RESIDENT
        WHERE RESIDENT.nursing_home_fk = %s;
        """,
            (user.nursing_home_id,),
        )


    resident_list = list()
    for index, (id,name,initial,last_name,m_last_name,img,birthday,dump1,dump2,dump3) in enumerate(cursor.fetchall()):
        resident_list.append(Resident(id, name, initial, last_name, m_last_name, img, birthday))
        resident_list[index].set_vitals_list(get_vitals(resident_list[index]))


    cursor.close()
    connection.close()

    return resident_list


def get_medication_list(resident):
    """
    Gets the list of medication for each requested resident
    """
    connection = connect_to_db()
    cursor = connection.cursor()

    cursor.execute(
        """
                SELECT MEDICATION.id_pk, MEDICATION.name,MEDICATION.half_life,PHARMACEUTICAL.dose,PHARMACEUTICAL.PILL_quantity,PHARMACEUTICAL.PILL_frequency,PHARMACEUTICAL.refill_quantity,PHARMACEUTICAL.start_date,PHARMACEUTICAL.perscription_date
                FROM MEDICATION
                INNER JOIN PHARMACEUTICAL on MEDICATION.id_pk = PHARMACEUTICAL.MEDICATION_pk_fk
                INNER JOIN RESIDENT on PHARMACEUTICAL.RESIDENT_pk_fk = RESIDENT.id_pk
                WHERE RESIDENT.id_pk = {0};
                   """.format(
                            resident.id
        )
    )
    medication_list = list()
    for index, (id,name,half_life,dosage,pill_quantity,pill_frequency,refill_quantity,start_date,perscription_date) in enumerate(cursor.fetchall()):
        medication_list.append(Medication(id,name,dosage,pill_quantity,pill_frequency,refill_quantity,start_date,perscription_date,half_life))

        medication_list[index].set_pill_list(
            get_pill_list(medication_list[index], resident)
        )

        medication_list[index].set_refill_list(
            get_refill_list(medication_list[index], resident)
        )

        medication_list[index].set_diagnosis_list(
            get_diagnosis_list(medication_list[index],resident)
        )
    cursor.close()
    connection.close()

    return medication_list

def get_diagnosis_list(medication,resident):
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(
        """
                SELECT DIAGNOSIS.id_pk, DIAGNOSIS.name
                FROM DIAGNOSIS
                INNER JOIN MEDICATION ON DIAGNOSIS.MEDICATION_fk = MEDICATION.id_pk
                INNER JOIN PHARMACEUTICAL on MEDICATION.id_pk = PHARMACEUTICAL.MEDICATION_pk_fk
                INNER JOIN RESIDENT ON PHARMACEUTICAL.RESIDENT_pk_fk = RESIDENT.id_pk
                WHERE MEDICATION.id_pk = {0} AND RESIDENT.id_pk = {1};
                   """.format(
            medication.id, resident.id
        )
    )
    diagnosis_list = list()
    for id , name in cursor.fetchall():
        diagnosis_list.append(Diagnosis(id,name))


    return diagnosis_list



def get_pill_list(medication, resident):
    """
    Gets the list of pills taken for each requested medication
    """
    connection = connect_to_db()
    cursor = connection.cursor()

    cursor.execute(
        """
                SELECT PILL.id_pk, PILL.taken_timestamp
                FROM PILL
                INNER JOIN PHARMACEUTICAL ON PILL.PHARMACEUTICAL_fk = PHARMACEUTICAL.id_pk
                INNER JOIN MEDICATION ON PHARMACEUTICAL.MEDICATION_pk_fk = MEDICATION.id_pk
                INNER JOIN RESIDENT ON PHARMACEUTICAL.RESIDENT_pk_fk = RESIDENT.id_pk
                WHERE MEDICATION.id_pk = {0} AND RESIDENT.id_pk = {1};
                   """.format(
            medication.id, resident.id
        )
    )
    pill_list = list()

    for id, taken_timestamp in cursor.fetchall():
        pill_list.append(Pill(id, taken_timestamp))

    return pill_list


def get_refill_list(medication, resident):
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(
        """
                    SELECT REFILL.id_pk, REFILL.timestamp
                    FROM REFILL
                    INNER JOIN PHARMACEUTICAL ON REFILL.PHARMACEUTICAL_fk = PHARMACEUTICAL.id_pk
                    INNER JOIN MEDICATION ON PHARMACEUTICAL.MEDICATION_pk_fk = MEDICATION.id_pk
                    INNER JOIN RESIDENT ON PHARMACEUTICAL.RESIDENT_pk_fk = RESIDENT.id_pk
                    WHERE MEDICATION.id_pk = {0} AND RESIDENT.id_pk = {1};
                   """.format(medication.id, resident.id))
    refill_list = list()

    for id, taken_timestamp in cursor.fetchall():
        refill_list.append(Refill(id, taken_timestamp))

    return refill_list


def get_next_pill_id():
    connection = connect_to_db()
    cursor = connection.cursor()

    cursor.execute(
        """
                SELECT id_pk 
                FROM PILL
                ORDER BY id_pk desc
                LIMIT 1;
                   """
    )
    id = None
    for num in cursor.fetchall():
        id = num

    return id[0] + 1

def get_next_refill_id():
    connection = connect_to_db()
    cursor = connection.cursor()

    cursor.execute(
        """
                SELECT id_pk 
                FROM REFILL
                ORDER BY id_pk desc
                LIMIT 1;
                   """
    )
    id = None
    for num in cursor.fetchall():
        id = num

    if id == None:
        return 3000

    return id[0] + 1

def get_pharama_id(medication, resident):
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(
        """
                SELECT PHARMACEUTICAL.id_pk
                FROM PHARMACEUTICAL
                INNER JOIN MEDICATION ON PHARMACEUTICAL.medication_pk_fk = MEDICATION.id_pk
                INNER JOIN RESIDENT ON PHARMACEUTICAL.resident_pk_fk = RESIDENT.id_pk
                WHERE MEDICATION.id_pk = {0} and RESIDENT.id_pk = {1};
                   """.format(medication.id, resident.id))

    id = None
    for num in cursor.fetchall():
        id = num

    return id[0]


def insert_into_pill(medication, resident, nurse):
    import datetime

    new_pill_id = get_next_pill_id()
    pharma_id = get_pharama_id(medication, resident)

    # Get the current datetime as a datetime object
    current_datetime = datetime.datetime.now()

    # Replace these with your actual values
    new_pill_id = get_next_pill_id()
    pharma_id = get_pharama_id(medication, resident)
    nurse_id = nurse.id

    # Assuming your connect_to_db() function returns a valid MySQL connection
    connection = connect_to_db()

    # Create a cursor
    cursor = connection.cursor()

    # Use placeholders for values in the SQL query
    insert_query = """
        INSERT INTO PILL
        VALUES (%s, %s, %s, %s)
    """
    
    # Execute the query with the data
    cursor.execute(insert_query, (new_pill_id, current_datetime, pharma_id, nurse_id))

    # Commit the changes to the database
    connection.commit()

    # Close the cursor and the database connection
    cursor.close()
    connection.close()
    return None

def insert_into_refill(medication, resident):
    import datetime

    # Get the current datetime as a datetime object
    current_datetime = datetime.datetime.now()

    # Replace these with your actual values
    new_refill_id = get_next_refill_id()
    pharma_id = get_pharama_id(medication, resident)

    # Assuming your connect_to_db() function returns a valid MySQL connection
    connection = connect_to_db()

    # Create a cursor
    cursor = connection.cursor()

    # Use placeholders for values in the SQL query
    insert_query = """
        INSERT INTO REFILL
        VALUES (%s, %s, %s)
    """
    
    # Execute the query with the data
    cursor.execute(insert_query, (new_refill_id, current_datetime, pharma_id))

    # Commit the changes to the database
    connection.commit()

    # Close the cursor and the database connection
    cursor.close()
    connection.close()
    return None



def get_all_medication_names():
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(
        """
                    SELECT DISTINCT name FROM MEDICATION order by 1 asc;
                   """
    )
    known_medication = []
    for name in cursor.fetchall():
        known_medication.append(name[0])

    return known_medication


def get_all_diagnosis_names():
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(
        """
                    SELECT DISTINCT name FROM DIAGNOSIS order by 1 asc;
                   """
    )
    known_diagnosis = []
    for name in cursor.fetchall():
        known_diagnosis.append(name[0])

    return known_diagnosis


def find_med_id(med_name):
    connection = connect_to_db()
    cursor = connection.cursor()
    # Use parameterized query to avoid SQL injection
    query = """
        SELECT DISTINCT id_pk
        FROM MEDICATION
        WHERE LOWER(name) = LOWER(%s)
    """

    cursor.execute(query, (med_name,))
    data = cursor.fetchall()

    if len(data) == 0:
        return 0
    else:
        return data[0]


def get_new_medication_id():
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(
        """
                SELECT id_pk 
                FROM MEDICATION
                ORDER BY id_pk desc
                LIMIT 1;
                   """
    )
    id = None
    for num in cursor.fetchall():
        id = num

    return id[0] + 1


def get_new_pharmaceutical_id():
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(
        """
                SELECT id_pk 
                FROM PHARMACEUTICAL
                ORDER BY id_pk desc
                LIMIT 1;
                   """
    )
    id = None
    for num in cursor.fetchall():
        id = num

    return id[0] + 1


def get_new_diagnosis_id():
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(
        """
                SELECT id_pk 
                FROM DIAGNOSIS
                ORDER BY id_pk desc
                LIMIT 1;
                   """
    )
    id = None
    for num in cursor.fetchall():
        id = num

    if id is None:
        id = 13000
        return id
    
    return id[0] + 1


def add_new_medication(resident,id,medication_name,route,dosage,pill_quantity,pill_frequency,refill_quantity,start_date,prescription_date,diagnosis_list):
    connection = connect_to_db()
    cursor = connection.cursor()

    if id == 0:
        id = get_new_medication_id()

        cursor.execute(
            """
                    INSERT INTO MEDICATION
                    VALUES ({0},{1},{2},{3})
                    """.format(
                id, medication_name, route,12
            )
        )

    # Use placeholders for values in the SQL query
    insert_query = """
        INSERT INTO PHARMACEUTICAL (id_pk,dose,pill_quantity,pill_frequency,refill_quantity,start_date,perscription_date,resident_pk_fk,medication_pk_fk)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                   """
    # Execute the query with the data
    cursor.execute(
        insert_query,
        (
            get_new_pharmaceutical_id(),
            dosage,
            pill_quantity,
            pill_frequency,
            refill_quantity,
            start_date,
            prescription_date,
            resident.id,
            id[0],
        )
    )

    

    insert_query = """
    INSERT INTO DIAGNOSIS (id_pk,name,medication_fk)
    VALUES(%s,%s,%s)
    """

    for diagnosis in diagnosis_list:
        # Execute the query with the data
        cursor.execute(insert_query,
            (
                get_new_diagnosis_id(),
                diagnosis,
                id[0]
            )
        )


    connection.commit()

    #resident.add_medication(Medication(id[0],medication_name,dosage,pill_quantity,pill_frequency,refill_quantity,start_date,prescription_date))
    # Close the cursor and the database connection
    cursor.close()
    connection.close()
    return None


def get_wellness_checks(resident):
    connection = connect_to_db()
    cursor = connection.cursor()

    cursor.execute("""
                   SELECT id_pk, timestamp,rating, description
                   FROM WELLNESS_CHECK
                   WHERE resident_fk = {0};
                   """.format(resident.id))
    
    wellness_info = []

    for id,time,rating,description in cursor.fetchall():
        wellness_info.append(Wellness_check(id,time,rating,description))

    cursor.close()
    connection.close()

    return wellness_info

def get_new_wellness_id():
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(
        """
                SELECT id_pk 
                FROM WELLNESS_CHECK
                ORDER BY id_pk desc
                LIMIT 1;
                   """
    )
    id = None
    for num in cursor.fetchall():
        id = num

    if id is None:
        id = 10000
        return id

    return id[0] + 1


def insert_wellness_check(wellness_check, resident,vitals =None):
    connection = connect_to_db()
    cursor = connection.cursor()

   # Use placeholders for values in the SQL query
    insert_query = """
        INSERT INTO WELLNESS_CHECK (id_pk,timestamp,rating,description,resident_fk)
        VALUES (%s,%s,%s,%s,%s)
    """
    wellness_check.id = get_new_wellness_id()

    # Execute the query with the data
    cursor.execute(
        insert_query,
        (
            wellness_check.id,
            wellness_check.timestamp,
            wellness_check.rating,
            wellness_check.description,
            resident.id,
        )
    )
    connection.commit()

    # Close the cursor and the database connection
    cursor.close()
    connection.close()

    if vitals:
        insert_vitals(vitals,wellness_check)
    return None

def get_new_vitals_id():
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(
        """
                SELECT id_pk 
                FROM VITALS
                ORDER BY id_pk desc
                LIMIT 1;
                   """
    )
    id = None
    for num in cursor.fetchall():
        id = num

    if id is None:
        id = 11000
        return id

    return id[0] + 1

def insert_vitals(vitals, wellness_check):
    connection = connect_to_db()
    cursor = connection.cursor()

   # Use placeholders for values in the SQL query
    insert_query = """
        INSERT INTO VITALS (id_pk,timestamp,temperature,weight,systolic_blood_pressure,diastolic_blood_pressure,heart_rate,glucose,wellness_check_fk)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    # Execute the query with the data
    cursor.execute(
        insert_query,
        (
            get_new_vitals_id(),
            vitals.timestamp,
            vitals.temperature,
            vitals.weight,
            vitals.systolic_blood_pressure,
            vitals.diastolic_blood_pressure,
            vitals.heart_rate,
            vitals.glucose,
            wellness_check.id,
        )
    )
    connection.commit()

    # Close the cursor and the database connection
    cursor.close()
    connection.close()
    return None

def get_vitals(resident):
    connection = connect_to_db()
    cursor = connection.cursor()

    cursor.execute("""
                    SELECT VITALS.id_pk,VITALS.timestamp, temperature, weight, systolic_blood_pressure,diastolic_blood_pressure,heart_rate,glucose
                   FROM VITALS 
                   INNER JOIN WELLNESS_CHECK ON VITALS.wellness_check_fk = WELLNESS_CHECK.id_pk
                   INNER JOIN RESIDENT ON WELLNESS_CHECK.resident_fk = RESIDENT.id_pk
                   WHERE RESIDENT.id_pk = {0};
                   """.format(resident.id))
    
    vitals_info = []

    for id, time, temp, weight,sys_blood_pressure,dia_blood_pressure,heart_rate,glucose in cursor.fetchall():
        vitals_info.append(Vitals(id,time,temp,weight,sys_blood_pressure,dia_blood_pressure,heart_rate,glucose))

    cursor.close()
    connection.close()

    return vitals_info

def get_new_caretaker_id():
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(
        """
                SELECT id_pk 
                FROM CARETAKER
                ORDER BY id_pk desc
                LIMIT 1;
                   """
    )
    id = None
    for num in cursor.fetchall():
        id = num

    if id is None:
        id = 4000
        return id

    return id[0] + 1


def create_new_caretaker(email, password,first_name,initial, paternal_last_name, maternal_last_name, phone_number):
    connection = connect_to_db()
    cursor = connection.cursor()
    phone_provider = "T-Mobil"
    id = get_new_caretaker_id()
    insert_query ="""
                   INSERT INTO CARETAKER(id_pk, email, password,first_name,initial,paternal_last_name,maternal_last_name,phone_number,phone_provider)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);
                   """
    cursor.execute(insert_query,(id,email,password,first_name,initial,paternal_last_name,maternal_last_name,phone_number,phone_provider))

    connection.commit()
    cursor.close()
    connection.close()
    return id


def get_new_resident_id():
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(
        """
                SELECT id_pk 
                FROM RESIDENT
                ORDER BY id_pk desc
                LIMIT 1;
                   """
    )
    id = None
    for num in cursor.fetchall():
        id = num

    if id is None:
        id = 0000
        return id

    return id[0] + 1


def create_new_resident(first_name,initial,paternal_last_name,maternal_last_name,image,birthday,height,caretaker_id,nursing_home_id):
    connection = connect_to_db()
    cursor = connection.cursor()
    id = get_new_resident_id()
    insert_query ="""
                   INSERT INTO RESIDENT(id_pk,first_name,initial,paternal_last_name,maternal_last_name,image,birthday,height,caretaker_fk,nursing_home_fk)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
                   """
    cursor.execute(insert_query,(id,first_name,initial,paternal_last_name,maternal_last_name,image,birthday,height,caretaker_id,nursing_home_id))

    connection.commit()
    cursor.close()
    connection.close()


def get_caretaker_phone_email():
    connection = connect_to_db()
    cursor = connection.cursor()

    cursor.execute("""
                SELECT email, phone_number 
                from CARETAKER;
                   """)
    email_list = []
    phone_list = []

    for email,phone in cursor.fetchall():
        email_list.append(email)
        phone_list.append(phone)


    return [email_list,phone_list]
