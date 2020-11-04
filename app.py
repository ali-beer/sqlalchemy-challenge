import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to the Hawaii Climate API!<br/>"
        f"Here you can access data on the weather station temperature observations (TOBS) and precipitation readings for Hawaii.<br/>"
        f"<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"To return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date:"
        f"<br/>"
        f"Please enter the start date in the format yyyy-m-d, e.g. /api/v1.0/2012-3-1<br/>"
        f"Route: /api/v1.0/<start><br/>"
        
        f"<br/>"
        f"To return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start and end date:"
        f"<br/>"
        f"Please enter the start date and end date in the format yyyy-m-d, e.g. /api/v1.0/2012-3-1/2015-3-1<br/>"
        f"Route: /api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query precipitation
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_ago).all()
    session.close()

    # Convert the query results to a dictionary using `date` as the key and `prcp` as the value
    prcp_dict = dict()

    for date, prcp in results:
        prcp_dict.setdefault(date, []).append(prcp)
    
    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():   
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query
    unique_stations = session.query(Measurement.station).\
        group_by(Measurement.station).all()
    session.close()

    # Convert list of tuples into normal list
    station_list = list(np.ravel(unique_stations))
    
    # Return a JSON list of stations from the dataset
    return jsonify(stations = station_list)
    

@app.route("/api/v1.0/tobs")
def tobs():    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query the dates and temperature observations of 
    # the most active station for the last year of data
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    active_station_12months = session.query(Measurement.tobs).\
        filter(Measurement.date >= year_ago).\
        filter(Measurement.station == 'USC00519281').all()
    session.close()   
    
    # Convert list of tuples into normal list
    active_station_list = list(np.ravel(active_station_12months))

    # Return a JSON list of temperature observations (TOBS) for the previous year
    return jsonify(TOBS = active_station_list)


@app.route("/api/v1.0/<start>")
def calc_temp_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for 
    # all dates greater than and equal to the start date.
    format_date = start.split("-")
    yyyy = int(format_date[0])
    m = int(format_date[1])
    d = int(format_date[2])
    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= dt.datetime(yyyy,m,d)).all()

    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date.
    return jsonify({f'Start date: {start}': [f'min temp: {results[0][0]}', f'avg temp: {results[0][1]}', f'max temp: {results[0][2]}']})
    

@app.route("/api/v1.0/<start>/<end>")
def calc_temp_date_range(start, end):
    # Create our session (Link) from Python to the DB
    session = Session(engine)
    
    # When given the start and the end date, calculate the `TMIN`, `TAVG`, 
    # and `TMAX` for dates between the start and end date inclusive.
    # Format start date 
    start_date = start.split("-")
    start_y = int(start_date[0])
    start_m = int(start_date[1])
    start_d = int(start_date[2])
    
    # Format end date
    end_date = end.split("-")
    end_y = int(end_date[0])
    end_m = int(end_date[1])
    end_d = int(end_date[2])
    
    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= dt.datetime(start_y,start_m,start_d)).\
            filter(Measurement.date <= dt.datetime(end_y,end_m,end_d)).all()
    
    # Return a JSON list of the minimum temperature, the average temperature, and 
    # the max temperature for a given start or start-end range.
    return jsonify({f'Date range: {start} to {end}': [f'min temp: {results[0][0]}', f'avg temp: {results[0][1]}', f'max temp: {results[0][2]}']})


if __name__ == '__main__':
    app.run(debug=True)