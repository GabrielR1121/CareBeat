from website.config import db
import pandas as pd 
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta



def createGraphOne(medication, resident):
    """
    Method to create the first Medication Adherence Rate (M.A.R.) using the amount of pills taken each day and the dates.
    This graph demonstrates how well the patient is being administered their medication
    Receives: 2 objects of Medication and resident.
    Returns: The figure object with all the correct data.
    """

    # From the database retrieve the needed data for this graph
    graph_df = pd.DataFrame.from_dict(db.get_graph1_data(medication, resident))

    # Create a scatter plot with lines connecting the dots
    fig = go.Figure(data=go.Scatter(x=graph_df["Date"], y=graph_df["Amount"], mode='lines+markers', name="Medication"))

    # Update the x-axis so that the dates are slanted
    fig.update_xaxes(tickangle=55)

    # Update the title of the graph so it's in the center
    fig.update_layout(title="Medication", title_x=0.5)

    return fig

def createGraphTwo(medication, resident):
    """
    Method to create the pill progression chart using the amount of pills taken
    This graph demonstrates how many pills are left in order to complete treatment in percantage values
    Receives: 2 objects of Medication and resident.
    Returns: The figure object with all the correct data.
    """
    #Gets the values neeeded to create the table from the database
    (medication_name,medication_taken,medication_total) = db.get_graph2_data(medication,resident)

    print()
    #Creates a gauge chart
    fig =  go.Figure(go.Indicator(
    mode = "gauge+number",
    value = (medication_taken/medication_total)*100,
    domain = {'x': [0, 1], 'y': [0, 1]},
    title = {'text': "{0} Progress".format(medication_name)},
    gauge = {'axis': {'range': [None, 100]} }))

    #Update the title of the graph so its in the center
    fig.update_layout(title_x=0.5)
    
    return fig



def createGraphThree(medication, resident):
    """
    Method to create the chart to see the amount of pills taken per month using the amount of pills taken
    This graph demonstrates how many pills were taken per month
    Receives: 2 objects of Medication and resident.
    Returns: The figure object with all the correct data.
    """

    #Retrieve the required data from the database
    graph_df = pd.DataFrame.from_dict(db.get_graph3_data(medication, resident))
    #Using the created DataFrame create a figure that has the correct values
    fig = px.bar(graph_df, x='Date', y='Amount', title="Month")

    #Update the title of the graph so its in the center
    fig.update_layout(title_x=0.5)

    return fig


    

def createGraphFour(medication, resident):
    """
    Method to create the Daily Medication Adherence Rate (M.A.R.) using the amount of pills taken each day and the dates in percentage values.
    This graph demonstrates how well the patient is being administered their medication
    Receives: 2 objects of Medication and resident.
    Returns: The figure object with all the correct data.
    """
    #From the database retrive the needed data for this graph
    graph_df = pd.DataFrame.from_dict(db.get_graph4_data(medication, resident))
    #Using the created DataFrame create a figure that has the correct values
    fig = px.line(graph_df,x="Date", y="Average", title= "Daily Medication Adherence Rate") 
    
    #Adds an aditional line to the graph to demonstrate the best expected adherence rate
    fig.add_trace(go.Scatter(x=graph_df["Date"], 
                         y=[90 for _ in range(graph_df["Date"].size)], 
                         mode='lines',
                         name='Target Adherence',
                         line=dict(color='red')))
    
    #Adds an aditional line to the graph to demonstrate the least expected adherence rate
    fig.add_trace(go.Scatter(x=graph_df["Date"], 
                         y=[80 for _ in range(graph_df["Date"].size)], 
                         mode='lines',
                         showlegend=False,
                         line=dict(color='red')))


    #Update the title of the graph so its in the center
    fig.update_layout(title_x=0.5)

    return fig

def createGraphFive(medication, resident):
    """
    Method to create the Weekly Medication Adherence Rate (M.A.R.) using the amount of pills taken each day and the dates in percentage values.
    This graph demonstrates how well the patient is being administered their medication
    Receives: 2 objects of Medication and resident.
    Returns: The figure object with all the correct data.
    """

    #From the database retrive the needed data for this graph
    graph_df = pd.DataFrame.from_dict(db.get_graph5_data(medication, resident))

    #Using the created DataFrame create a figure that has the correct values
    fig = px.line(graph_df, x="Week", y="Average", title="Weekly MAR")

    #Adds an aditional line to the graph to demonstrate the best expected adherence rate
    fig.add_trace(go.Scatter(x=graph_df["Week"], 
                         y=[90 for _ in range(graph_df["Week"].size)], 
                         mode='lines',
                         name='Target Adherence',
                         line=dict(color='red')))
    
    #Adds an aditional line to the graph to demonstrate the least expected adherence rate
    fig.add_trace(go.Scatter(x=graph_df["Week"], 
                         y=[80 for _ in range(graph_df["Week"].size)], 
                         mode='lines',
                         showlegend=False,
                         line=dict(color='red')))
    
    #Update the title of the graph so its in the center
    fig.update_layout(title_x=0.5)

    return fig

def createGraphSix(medication, resident):
    """
    Method to create the Monthly Medication Adherence Rate (M.A.R.) using the amount of pills taken each day and the dates in percentage values.
    This graph demonstrates how well the patient is being administered their medication
    Receives: 2 objects of Medication and resident.
    Returns: The figure object with all the correct data.
    """
    #From the database retrive the needed data for this graph
    graph_df = pd.DataFrame.from_dict(db.get_graph6_data(medication, resident))
    #Using the created DataFrame create a figure that has the correct values
    fig = px.line(graph_df, x='Date', y='Amount', title="Month")
     #Adds an aditional line to the graph to demonstrate the best expected adherence rate
    fig.add_trace(go.Scatter(x=graph_df["Date"], 
                         y=[90 for _ in range(graph_df["Date"].size)], 
                         mode='lines',
                         name='Target Adherence',
                         line=dict(color='red')))
     #Adds an aditional line to the graph to demonstrate the least expected adherence rate
    fig.add_trace(go.Scatter(x=graph_df["Date"], 
                         y=[80 for _ in range(graph_df["Date"].size)], 
                         mode='lines',
                         showlegend=False,
                         line=dict(color='red')))
    
    #Update the title of the graph so its in the center
    fig.update_layout(title_x=0.5)
    
    return fig

def createGraphSeven(medication, resident):
    """
    Method to create the supply forecast chart using the amount of pills taken
    This graph demonstrates how many pills are left in order to complete treatment and alerts when medications are running low
    Receives: 2 objects of Medication and resident.
    Returns: The figure object with all the correct data.
    """
    #Gets the values neeeded to create the table from the database
    (medication_name, medication_taken, medication_total) = db.get_graph7_data(medication, resident)

    #Creates the warning values and it auto adjusts depending on the medication
    danger_warning = medication_total * 0.2
    yellow_warning = medication_total/2
    green_warning = medication_total

    #Creates the gauge chart
    fig = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = medication_total - medication_taken,
    domain = {'x': [0, 1], 'y': [0, 1]},
    title = {'text': "{0} Supply Forecast".format(medication_name)},
    gauge = {'axis': {'range': [None, medication_total]},
             'bar': {'color': "darkgreen"},
             'steps' : [
                 {'range': [0, danger_warning], 'color': "lightcoral"},
                 {'range': [danger_warning, yellow_warning], 'color': "lightyellow"},
                 {'range': [yellow_warning, green_warning], 'color': "lightgreen"}
                  ]}))
    #Update the title of the graph so its in the center
    fig.update_layout(title_x=0.5)

    return fig

def createGraphEight(medication, resident):
    from decimal import Decimal
    """
    Method to create the Daily Dose Average chart using the amount of doses taken and the dates
    This graph demonstrates how consistent the daily dosage goals are being met
    Receives: 2 objects of Medication and resident.
    Returns: The figure object with all the correct data.
    """
    #Retrieves the data from the database
    graph_df = pd.DataFrame.from_dict(db.get_graph8_data(medication,resident))

    prescribed_daily_dose = medication.get_perscription_daily_dose()
    print("Perscribed_d_dose" + str(prescribed_daily_dose))
    

    #Creates a line chart with the given data
    fig = px.line(graph_df, x="Date", y="Dose (mg)", title="Daily Dose Average")

    #Adds a line that shows the max exppected dosage per day
    fig.add_trace(go.Scatter(x=graph_df["Date"], 
                             y=[prescribed_daily_dose for x in range(graph_df["Date"].size)], 
                             mode='lines',
                             name="Prescribed Dose",
                             line=dict(color='red')))
    #Adds a line that shows the min expected dosage per day
    fig.add_trace(go.Scatter(x=graph_df["Date"], 
                             y=[Decimal(prescribed_daily_dose)*Decimal(0.8) for x in range(graph_df["Date"].size)], 
                             mode='lines',
                             showlegend=False,
                             line=dict(color='red')))

    #Update the title of the graph so its in the center
    fig.update_layout(title_x=0.5)

    return fig

def createGraphNine(medication,resident):
    '''
    This Graph is meant to visualize a correct medication intake and what the patient is actually receiving. 
    The dotted line represents a prediction of when the medication will end based on missed medications
    '''
    #Retrieves the data from the database
    graph_df = pd.DataFrame.from_dict(db.get_graph9_data(medication, resident))

    # Starts the medication one day before to ensure all graphs have a (0,0) starting coords
    start_date = medication.start_date - timedelta(1)

    #This is the estimated iniial start date if the treatment is administered perfectly.
    estimated_end_date = medication.get_estimated_end_date().date()

    #The total amount of pills this medication has 
    total_pills = medication.pill_quantity
    #The frequency at which each person needs to drink their medication
    daily_pills = medication.pill_frequency
    #List to store the expected dates in which the medication will be consumed
    dates_expected = []
    #The expected amount of cumulative pills the patient needs to consume daily
    expected_cumulative_pills = []
    #Stores the start date in order to reach the exact date the medication will end
    current_date = start_date.date()
    #Stores the exact number of daily cumulative pills in order to record the exact number
    cumulative_pills =0

    #This while loop is an application of numerical analysis where the goal is to reach the EXACT day and cumulative pills taken daily
    # This is because if the frequency divided by the total is a fraction the amount of pills will either be over or under
    # This ensures the count is exact.
    while cumulative_pills < medication.pill_quantity and current_date <= estimated_end_date:
            dates_expected.append(current_date)
            expected_cumulative_pills.append(cumulative_pills)
            cumulative_pills += daily_pills
            current_date += timedelta(days=1)

    # Add the final data point at the estimated end date
    if current_date <= estimated_end_date:
        dates_expected.append(estimated_end_date)
        expected_cumulative_pills.append(medication.pill_quantity)

    # Converts the Date dictionary into a list in order to add the starting (0,0) value
    dates_actual = graph_df['Date'].tolist()
    dates_actual.insert(0,start_date)
    #Converts the Amount dictionary into a list in order to add the starting (0,0) value
    actual_cumulative_pills = graph_df['Amount'].cumsum().tolist()
    actual_cumulative_pills.insert(0, 0)

    # Calculate a new estimated end date based on actual intake
    # Gets a new end date based on the last date the medication was administered
    actual_end_date = dates_actual[-1]
    new_estimated_end_date = actual_end_date + timedelta(days=(total_pills - actual_cumulative_pills[-1]) / daily_pills)

    # Check if the new estimated end date is in the past
    if new_estimated_end_date < actual_end_date:
        # If it's in the past, set it to the actual end date
        new_estimated_end_date = actual_end_date

    # Create data points for the dotted line (new estimated end date)
    dates_dotted = [actual_end_date + timedelta(days=i) for i in range((new_estimated_end_date - actual_end_date).days + 1)]
    dotted_cumulative_pills = [actual_cumulative_pills[-1] + i * daily_pills for i in range(len(dates_dotted))]

    # Create Plotly traces
    trace_expected = go.Scatter(x=dates_expected, y=expected_cumulative_pills, mode='lines', name='Expected Intake')
    trace_actual = go.Scatter(x=dates_actual, y=actual_cumulative_pills, mode='lines', name='Actual Intake')
    trace_dotted = go.Scatter(x=dates_dotted, y=dotted_cumulative_pills, mode='lines+markers', name='New Estimated Intake')

    # Calculate the deviation between the last two dates in "Expected" and "Actual"
    last_expected_cumulative = expected_cumulative_pills[-1]
    last_actual_cumulative = dotted_cumulative_pills[-1]
    deviation = last_expected_cumulative - last_actual_cumulative

    # Calculate the percentage deviation
    percentage_deviation = (deviation / last_expected_cumulative) * 100

    # Check if the percentage deviation is less than 5%
    if percentage_deviation < 5:
        print("Percentage deviation is less than 5%. The Deviation is {0}".format(percentage_deviation))
    else:
        print("Percentage deviation is 5% or higher. The Deviation is {0}".format(percentage_deviation))

    # Create the layout for the chart
    layout = go.Layout(
        title='Medication Intake',
        xaxis=dict(title='Date'),
        yaxis=dict(title='Cumulative Pills Taken')
    )

    # Create the Plotly figure
    fig = go.Figure(data=[trace_expected, trace_actual, trace_dotted], layout=layout)
    return fig

def createGraphTen(medication, resident):
    graph_df = pd.DataFrame.from_dict(db.get_graph10_data(medication, resident))

    days = []  # Use an empty list to store day numbers
    count = 0  # Start counting from 0

    import datetime

    # Check if the DataFrame is empty
    if graph_df.empty:
        current_value = datetime.date.today()
        current_hour = datetime.datetime.now().hour
        days = [0]
        hours = [current_hour]
        concentrations = [0]
    else:
        current_value = graph_df['Dates'].iloc[0]
        hours = graph_df['Hour']
        concentrations = [float(conc) for conc in graph_df['Dose']]  # Convert to float

    for dates in graph_df['Dates']:
        if current_value == dates:
            days.append(count)
        else:
            count += 1
            current_value = dates
            days.append(count)

    # Initialize variables to store daily AUC and half-life values
    daily_auc_values = []
    daily_half_life_values = []

    # Calculate AUC and half-life for each day
    for day in range(max(days) + 1):  # Adjust the loop to start at 0
        # Filter data for the current day
        day_indices = [i for i, d in enumerate(days) if d == day]
        day_hours = [hours[i] for i in day_indices]
        day_concentrations = [concentrations[i] for i in day_indices]

        # Calculate daily AUC using the trapezoidal rule
        daily_auc = 0
        for i in range(1, len(day_hours)):
            delta_t = day_hours[i] - day_hours[i - 1]
            avg_concentration = (day_concentrations[i] + day_concentrations[i - 1]) / 2
            daily_auc += delta_t * avg_concentration

        # Calculate daily half-life (assuming first-order kinetics)
        try:
            if day_concentrations[0] != 0:  # Avoid division by zero
                daily_half_life = -0.693 / (day_concentrations[-1] / day_concentrations[0])
            else:
                daily_half_life = 0
        except ZeroDivisionError:
            daily_half_life = 0

        daily_auc_values.append(daily_auc)
        daily_half_life_values.append(daily_half_life)

    # Create a Plotly figure for the daily AUC values
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(range(max(days) + 1)), y=daily_auc_values, mode='lines+markers', name='Daily AUC'))

    # Configure the layout
    fig.update_layout(
        title='Daily AUC of Drug Concentration-Time Curve',
        xaxis_title='Day',
        yaxis_title='Daily AUC (mg*hr/mL)',
    )

    # Print the estimated daily half-life values
    for day, half_life in enumerate(daily_half_life_values):
        print(f"Day {day}: Estimated Half-Life = {half_life:.2f} hours")

    return fig