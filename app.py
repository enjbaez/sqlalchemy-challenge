# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 12:00:41 2020

@author: ebaez
"""

import numpy as np
import sqlalchemy
import datetime as dt
import datetime as datetime
from datetime import timedelta
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False}, echo=True)
# reflect existing database 
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

app = Flask(__name__)
  

@app.route("/")
def welcome():
    """List all available api routes."""
    return """<html> 
<h1>List of all available Honolulu, Hawaii API routes</h1>

        <li>
        <a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a>
        </li>
        <br>
        <li>
        <a href="/api/v1.0/stations">/api/v1.0/stations</a>
        </li>
        <br>
        <li>
        <a href="/api/v1.0/tobs">/api/v1.0/tobs</a>
        </li>
        <br>
        <li>
        <a href="/api/v1.0/2020-01-01">/api/v1.0/2020-01-01</a>
        </li>
        <br>
        <li>
        <a href="/api/v1.0/2020-01-07">/api/v1.0/2020-01-07</a>
        </li>
        </br>

</html>
    """

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of precipitations from last year"""
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    max_date = max_date[0]

    year_ago = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=366)
    
    results_precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()

    precipitation_dict = dict(results_precipitation)

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations(): 
    """Return a JSON list of stations from the dataset."""
    results_stations =  session.query(Measurement.station).group_by(Measurement.station).all()

    stations_list = list(np.ravel(results_stations))

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs(): 
    """Return a JSON list of Temperature Observations (tobs) for the previous year."""

    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    max_date = max_date[0]

    year_ago = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=366)

    results_tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).all()

    tobs_list = list(results_tobs)

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def temperature_s(start):
    # Set start and end dates for date range
    startDate = datetime.datetime.strptime("2017-08-01", "%Y-%m-%d")
    endDate = datetime.datetime.strptime("2017-08-23", "%Y-%m-%d")

    # Date range
    # Getting date range
    delta = endDate - startDate
    date_range = []
    for i in range(delta.days + 1):
        date_range.append(startDate + timedelta(days=i))
    
    # Converting to strings to filter
    str_date_range = []
    for date in date_range:
        new_date = date.strftime("%Y-%m-%d")
        str_date_range.append(new_date)

    # Grabbing avg, min & max temps    
    temp_avg = session.query(func.avg(Measurement.tobs))\
                .filter(Measurement.date.in_(str_date_range))[0][0]
    temp_min = session.query(func.min(Measurement.tobs))\
                .filter(Measurement.date.in_(str_date_range))[0][0]
    temp_max = session.query(func.max(Measurement.tobs))\
                .filter(Measurement.date.in_(str_date_range))[0][0]

    # Dictionary of temperatures
    temp_dict = {}
    temp_dict["Average Temperature"] = temp_avg
    temp_dict["Minimum Temperature"] = temp_min
    temp_dict["Maximum Temperature"] = temp_max

    return jsonify(temp_dict)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):

    """Return a JSON list of tmin, tmax, tavg for the dates in range of start date and end date inclusive"""
    
    between_dates = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    between_dates_list=list(between_dates)
    return jsonify(between_dates_list)

if __name__ == '__main__':
    app.run(debug=True)