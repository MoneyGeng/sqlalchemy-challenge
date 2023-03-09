# import dependencies
import datetime as dt
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#reflect database into new model
Base = automap_base()
Base.prepare(autoload_with=engine)
Measurement = Base.classes.measurement
Station = Base.classes.station

# flask setup
app = Flask(__name__)

@app.route("/")
def home():
    """List available api routes."""
    return (
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/&lt;start&gt;<br/>"
        "/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    # Create a session and query for precipitation data
    session = Session(engine)
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    last_year_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d').date() - dt.timedelta(days=365)
    
    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_year_date).\
        order_by(Measurement.date).all()
    
    session.close()

    # Convert the query results to a dictionary with date as the key and prcp as the value
    precipitation_dict = {}
    for date, prcp in results:
        precipitation_dict[date] = prcp
    
    # Return the JSON representation of the dictionary
    return jsonify(precipitation_dict)

@app.route('/api/v1.0/stations')
def stations():

    # Create a session and query for station data
    session = Session(engine)

    # Retrieve station data from the database.
    results = session.query(Station.id, Station.station, Station.name).\
        order_by(Station.id).\
        all()

    # Close the session
    session.close()

    # Create a list of dictionaries to store the station data.
    stations_list = []
    for id, station, name in results:
        station_dict = {}
        station_dict['id'] = id
        station_dict['station'] = station
        station_dict['name'] = name
        stations_list.append(station_dict)

    # Return the station data as a JSON object.
    return jsonify(stations_list)

@app.route('/api/v1.0/tobs')
def tobs():
    # Create a session and query for measurement data
    session = Session(engine)

    # Calculate the most recent date and the date a year ago from it
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    last_year_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d').date() - dt.timedelta(days=365)

    # Retrieve temperature observation data for the last year from the specified station
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= last_year_date).\
        filter(Measurement.station == 'USC00519281').\
        order_by(Measurement.date).\
        all()
    
    # Close the session
    session.close()

    # Create a dictionary to store date and temperature observation data and jsonify it
    tobs_dict = {}
    for date, tob in results:
        tobs_dict[date] = tob
        
    return jsonify(tobs_dict)

@app.route('/api/v1.0/<start>')
def start_temps(start):
    # Create a session and query for temperature data
    session = Session(engine)

    # Convert the start date string to a datetime object
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()

    # Perform a query to retrieve the minimum, maximum, and average temperatures for dates greater than or equal to the start date
    results = session.query(func.min(Measurement.tobs), 
                            func.max(Measurement.tobs), 
                            func.avg(Measurement.tobs)).\
                            filter(Measurement.date >= start_date).all()

    # Close the session
    session.close()

    # Create a dictionary to store the temperature data and jsonify it
    temps_dict = {}
    temps_dict['min_temp'] = results[0][0]
    temps_dict['max_temp'] = results[0][1]
    temps_dict['avg_temp'] = results[0][2]

    return jsonify(temps_dict)

@app.route('/api/v1.0/<start>/<end>')
def start_end_temps(start, end):
    # Convert the start and end date strings to datetime objects
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    end_date = dt.datetime.strptime(end, '%Y-%m-%d').date()

    # Create a session and query for temperature data
    session = Session(engine)
    
    # Perform a query to retrieve the minimum, maximum, and average temperatures for dates between the start and end dates (inclusive)
    results = session.query(func.min(Measurement.tobs), 
                            func.max(Measurement.tobs), 
                            func.avg(Measurement.tobs)).\
                            filter(Measurement.date >= start_date).\
                            filter(Measurement.date <= end_date).all()

    # Close the session
    session.close()

    # Create a dictionary to store the temperature data and jsonify it
    temps_dict = {}
    temps_dict['min_temp'] = results[0][0]
    temps_dict['max_temp'] = results[0][1]
    temps_dict['avg_temp'] = results[0][2]

    return jsonify(temps_dict)