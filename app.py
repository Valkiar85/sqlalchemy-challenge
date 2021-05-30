# Import Dependencies

import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

# Database Setup

engine = create_engine("sqlite:///hawaii.sqlite")

# Reflect an existing database into a new model

Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect = True)

# Save reference to each table

Measurement = Base.classes.measurement
Station = Base.classes.station

# Create an app, being sure to pass __name__

app = Flask(__name__)

# Define what to do when the user hits the index route

@app.route("/")
def home():

    # List all avaialble API routes

    return(
        f"Welcome to the Hawaii API!<br/>"
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&ltstart&gt<br/>"
        f"/api/v1.0/&ltstart&gt/&ltend&gt"
        
            )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Convert the query results to a dictionary using date as the key and prcp as the value.

    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    base_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    data_prcp = session.query(Measurement.date, Measurement.prcp).\
            filter(Measurement.date >= base_date).order_by(Measurement.date).all()

    session.close()
    
    prcp_dict = dict(data_prcp)

    # Return the JSON representation of your dictionary.

    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Return a JSON list of stations from the dataset.
    
    query_stations = session.query(Station.name, Station.station).all()

    # Dictionary to JSON

    station_list = []

    for station in query_stations:

        dict_station = {}

        dict_station['Name'] = station[0]
        dict_station['Station'] = station[1]
        station_list.append(dict_station)

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the dates and temperature observations of the most active station for the last year of data.

    # Query Most Active Station

    most_active_station = session.query(Measurement.station,func.count(Measurement.station)).\
    group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()

    # Query most recent date
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Return a JSON list of temperature observations (TOBS) for the previous year.

    temperature_observations = session.query(Station.name, Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= "2016-08-23", Measurement.date <= "2017-08-23").all()

    # Use dictionary, create json

    tobs_list = []

    for tob in temperature_observations:    
        
        dict_tob = {}
        dict_tob["Station"] = tob[0]
        dict_tob["Date"] = tob[1]
        dict_tob["Temperature"] = int(tob[2])
        tobs_list.append(dict_tob)

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def temperature_start(start):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Dates
    results_dates = session.query(Measurement.date).group_by(Measurement.date).all()

    all_dates = list(np.ravel(results_dates))


    if start in all_dates:
        tobs_results = session.query(Measurement.tobs).filter(Measurement.date >= start).\
            group_by(Measurement.tobs).all()

    # Return a JSON list of the minimum temperature, the average temperature, 
    # and the max temperature for a given start or start-end range.

        temperatures = list(np.ravel(tobs_results))

        low_temperature = min(temperatures)
        high_temperature = max(temperatures)
        average_temperature = sum(temperatures) / len(temperatures)

        session.close()


        return jsonify(f"The minimum temperature is {low_temperature}, \
            the high temperature is {high_temperature} and the average temperature is \
                {average_temperature}")

    else:
        return jsonify(f"Your date was not found")

@app.route("/api/v1.0/<start>/<end>")
def temperature_start_end(start,end):

     # Create our session (link) from Python to the DB
    session = Session(engine)

    # Dates
    results_dates = session.query(Measurement.date).group_by(Measurement.date).all()

    all_dates = list(np.ravel(results_dates))

    if (start) in all_dates:
        if (end) in all_dates: 
            tobs_results = session.query(Measurement.tobs).\
                filter(Measurement.date >= start).\
                filter(Measurement.date <= end).\
                group_by(Measurement.tobs).all()

    # Return a JSON list of the minimum temperature, the average temperature, 
    # and the max temperature for a given start or start-end range.

            temperatures = list(np.ravel(tobs_results))

            low_temperature = min(temperatures)
            high_temperature = max(temperatures)
            average_temperature = sum(temperatures) / len(temperatures)

            session.close()

            return jsonify(f"The minimum temperature is {low_temperature}, \
            the high temperature is {high_temperature} and the average temperature is \
                {average_temperature}")

        else:
            return jsonify(f"Your date was not found")

    else:
        return jsonify(f"Your date was not found")

if __name__ == "__main__":
    app.run(debug=True)