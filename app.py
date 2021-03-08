# 1. import Flask and other libraries
from flask import Flask, jsonify, render_template, request
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

################################################################################################################

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
conn = engine.connect()

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

################################################################################################################

# 2. Create an app, being sure to pass __name__
app = Flask(__name__)


################################################################################################################

# find out last year

last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
max_date = dt.datetime.strptime(last_date, "%Y-%m-%d")

# Calculate the date one year from the last date in data set.
last_year = max_date - dt.timedelta(days=365)

################################################################################################################

# 3. Define routes
@app.route("/")
def home():
    return render_template('index.html')


"""Return the JSON representation of your dictionary using date as the key and prcp as the value """
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    session = Session(engine)

    # Perform a query to retrieve the data and precipitation scores
    prcp_results = (
        session.query(Measurement.date, Measurement.prcp)
        .filter(Measurement.date > last_year)
        .order_by(Measurement.date)
        .all()
    )
    # Save the query results as a dictionary with the date as the key and the prcp record as the value
    # Return the valid JSON response object
    return jsonify(prcp_results)


"""Return a JSON list of stations from the dataset. """
@app.route("/api/v1.0/stations")
def stations():
    
    session = Session(engine)

    # find out station list
    station_list = session.query(Station.station, Station.name).all()

    # Save the query results as a dictionary with the date as the key and the prcp record as the value
    # Return the valid JSON response object
    return jsonify(station_list)


"""Return a JSON list of temperature observations (TOBS) for the previous year.
   Query the dates and temperature observations of the most active station for the last year of data. """
@app.route("/api/v1.0/tobs")
def tobs():
    
    session = Session(engine)

    # Get the most active station
    most_active_station = (
        session.query(Measurement.station, func.count(Measurement.station))
        .filter(Measurement.station == Station.station)
        .group_by(Measurement.station)
        .order_by(func.count(Measurement.station).desc())
        .first()
    )

    tobs_for_last_year = (
        session.query(Measurement.date, Measurement.tobs)
        .filter(Measurement.date > last_year) ### Last year
        .filter(Measurement.station == most_active_station[0]) ### Most active station
        .order_by(Measurement.date)
        .all()
    )

    # Save the query results as a dictionary with the date as the key and the prcp record as the value
    # Return the valid JSON response object
    return jsonify(tobs_for_last_year)


""" Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date """
@app.route("/api/v1.0/<start>")
def start(start):

    session = Session(engine)

    start_date = (
        session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
        )
        .filter(Measurement.date >= start)
        .all()
    )

    # Create a list to store the temperature records
    start_date_list = []
    start_date_dict = {"Start Date": start}
    start_date_list.append(start_date_dict)
    start_date_list.append(
        {"Observation": "Minimum Temperature", "Temperature(F)": start_date[0][0]}
    )
    start_date_list.append(
        {"Observation": "Average Temperature", "Temperature(F)": start_date[0][1]}
    )
    start_date_list.append(
        {"Observation": "Maximum Temperature", "Temperature(F)": start_date[0][2]}
    )

    return jsonify(start_date_list)


""" Return a JSON list of the minimum temperature, the average temperature, and the max temperature 
    between the start and end date inclusive """
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    session = Session(engine)

    start_end_date = (
        session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
        )
        .filter(Measurement.date >= start)
        .filter(Measurement.date <= end)
        .all()
    )

    # Create a list to store the temperature records
    start_end_date_list = []
    start_end_date_dict = {"Start Date": start, "End Date": end}
    start_end_date_list.append(start_end_date_dict)
    start_end_date_list.append(
        {"Observation": "Minimum Temperature", "Temperature(F)": start_end_date[0][0]}
    )
    start_end_date_list.append(
        {"Observation": "Average Temperature", "Temperature(F)": start_end_date[0][1]}
    )
    start_end_date_list.append(
        {"Observation": "Maximum Temperature", "Temperature(F)": start_end_date[0][2]}
    )

    return jsonify(start_end_date_list)


if __name__ == "__main__":
    app.run(debug=True)
