# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session


#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# reflect the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Save references to each table
# Measurement = Base.classes.measurement
# Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# Home route
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year ago from the last date in dataset
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the precipitation data for the last 12 months
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()
    
    # Convert the query results to a list
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

# Stations route
@app.route("/api/v1/0/stations")
def stations():
    # Query all stations
    results = session.query(Station.station).all()

    # Convert the query results to a list
    all_stations = [station[0] for station in results]
    return jsonify(all_stations)

# TOBS route
@app.route("/api/v1.0/tobs")
def tobs():
    #Query the temperature observations for the most active station for the last year of data
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= one_year_ago).all()
    
    # Convert the query results to a list
    temps_list = list(np.ravel(results))
    return jsonify(temps_list)

# Start and end date routes
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    if end:
        # Query min, avg, and max temperatures for the specified date range
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), 
                                func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
    else:
        # If no end date is provided, just query from the start date onward
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),
                                func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
        
    # Convert the query results to a list
    temps = list(np.ravel(results))

    return jsonify(temps)
if __name__ == '__main__':
    app.run(debug=True)
                