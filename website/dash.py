from website.config.config import db_config
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

    #From the database retrive the needed data for this graph
    graph_df = pd.DataFrame.from_dict(db.get_graph1_data(medication,resident))
    #Using the created DataFrame create a figure that has the correct values
    fig = px.line(graph_df,x="Date",y="Amount",title="Medication")

    #Update the x-axis so that the dates are slanted
    fig.update_xaxes(tickangle=55)

    #Update the title of the graph so its in the center
    fig.update_layout(title_x=0.5,autosize=True)

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

    #Updates the figure to allow auto resizing
    fig.update_layout(autosize = True)

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
    #Update the figure to allow auto resizing
    fig.update_layout(autosize=True)
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
    
    return fig

def createGraphSeven(medication, resident):
    """
    Method to create the supply forecast chart using the amount of pills taken
    This graph demonstrates how many pills are left in order to complete treatment and alerts when medications are running low
    Receives: 2 objects of Medication and resident.
    Returns: The figure object with all the correct data.
    """
    #Gets the values neeeded to create the table from the database
    (medication_name, medication_taken, medication_total, start_date,pill_frequency) = db.get_graph7_data(medication, resident)

    #Estimates when the medication will run out. this will mostlikely change in the future
    estimated_end_date = start_date + timedelta(days=medication_total/pill_frequency)

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
    return fig

def createGraphEight(medication, resident):
    """
    Method to create the Daily Dose Average chart using the amount of doses taken and the dates
    This graph demonstrates how consistent the daily dosage goals are being met
    Receives: 2 objects of Medication and resident.
    Returns: The figure object with all the correct data.
    """
    #Retrieves the data from the database
    data = db.get_graph8_data(medication, resident)
    prescribed_daily_dose = data[1]
    prescribed_daily_dose = int(prescribed_daily_dose)
    graph_df = pd.DataFrame.from_dict(data[0])

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
                             y=[prescribed_daily_dose*0.8 for x in range(graph_df["Date"].size)], 
                             mode='lines',
                             showlegend=False,
                             line=dict(color='red')))



    return fig

    



