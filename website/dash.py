from website.config import db
import pandas as pd 
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta,datetime
import math
from decimal import Decimal,getcontext



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



def createGraphNine(medication, resident):
    # Retrieve the data from the database
    graph_df = pd.DataFrame.from_dict(db.get_graph9_data(medication, resident))

    # Start the medication one day before to ensure all graphs have a (0,0) starting coords
    start_date = (medication.start_date - timedelta(1)).date()

    # This is the estimated initial start date if the treatment is administered perfectly.
    estimated_end_date = medication.get_estimated_end_date().date()
    print(estimated_end_date)

    # The total amount of pills this medication has
    total_pills = medication.pill_quantity
    # The frequency at which each person needs to take their medication
    daily_pills = medication.pill_frequency

    # Create data points for the expected intake (a straight line)
    dates_expected = [start_date + timedelta(days=i) for i in range((estimated_end_date - start_date).days)]  # Include the endpoint
    expected_cumulative_pills = [i * daily_pills for i in range(len(dates_expected))]

    # Convert the Date dictionary into a list to add the starting (0,0) value
    dates_actual = graph_df['Date'].tolist()
    dates_actual.insert(0, start_date)
    # Convert the Amount dictionary into a list to add the starting (0,0) value
    actual_cumulative_pills = graph_df['Amount'].cumsum().tolist()
    actual_cumulative_pills.insert(0, 0)

    # Calculate a new estimated end date based on actual intake
    actual_end_date = dates_actual[-1]
    new_estimated_end_date = actual_end_date + timedelta(days=(total_pills - actual_cumulative_pills[-1]) / daily_pills)
    print(new_estimated_end_date)

    # Check if the new estimated end date is in the past
    if new_estimated_end_date < actual_end_date:
        # If it's in the past, set it to the actual end date
        new_estimated_end_date = actual_end_date

    # Create data points for the dotted line (new estimated end date)
    dates_dotted = [actual_end_date + timedelta(days=i) for i in range((new_estimated_end_date - actual_end_date).days + 1)]
    dotted_cumulative_pills = [actual_cumulative_pills[-1] + i * daily_pills for i in range(len(dates_dotted))]

    # Create Plotly traces
    trace_expected = go.Scatter(x=dates_expected, y=expected_cumulative_pills, mode='lines+markers', name='Expected Intake')  # Add markers to the expected intake
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
    half_life_hours = 14  # Adjust the half-life as needed

    # Calculate the decay rate based on half-life
    decay_rate = math.log(1/2) / half_life_hours

    # Define your intake timestamps as datetime objects
    

    # Create a function to calculate drug concentration over time with spikes for each intake
    def calculate_concentration(time_stamps, decay_rate, intake_timestamps):
        concentration = []
        current_concentration = 0.0

        # Define a time step factor to control the rate of decay
        time_step_factor = 0.9  # Adjust as needed; smaller values result in slower decay

        for t in time_stamps:
            # Check if there is an intake event at this time
            if any(
                t.hour == ts.hour and t.day == ts.day and t.month == ts.month and t.year == ts.year
                for ts in intake_timestamps
            ):
                current_concentration = 100.0  # Spike to 100% when intake occurs

            # Apply decay with a controlled time step
            current_concentration *= math.exp(decay_rate * time_step_factor)
            concentration.append(current_concentration)

        return concentration

    # Calculate drug concentrations over time using the updated function
    concentration_values = calculate_concentration(time_stamps, decay_rate, intake_timestamps)

    # Create a Plotly chart to visualize the drug concentration over time
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=time_stamps, y=concentration_values, mode='lines', name='Drug Concentration'))

    # Set the y-axis label to indicate it's in percentages
    fig.update_layout(
        title='Drug Concentration Over Time',
        xaxis_title='Time',
        yaxis_title='Concentration (%)',
    )
    return fig