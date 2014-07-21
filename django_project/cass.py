import datetime
from uuid import uuid1, UUID
import random

from threading import Event

from cassandra.cluster import Cluster

cluster = Cluster(['127.0.0.1'])
session = cluster.connect('iotdb')

# Setting these globally reduces cass overhead
get_timestream_query = None
get_day_query = None
add_data_insert = None
add_data_pt_insert = None

class PagedResultHandler(object):

    def __init__(self, future):
        self.error = None
        self.finished_event = Event()
        self.future = future
        self.future.add_callbacks(
            callback=self.handle_page,
            errback=self.handle_error)

    def handle_page(self, rows):
        #for row in rows:
            #process_row(row)
			#pass

        if self.future.has_more_pages:
            self.future.start_fetching_next_page()
        else:
            self.finished_event.set()

    def handle_error(self, exc):
        self.error = exc
        self.finished_event.set()


class DatabaseError(Exception):
	"""
	The base error that functions in this module will raise when things go 
	wrong
	"""
	pass

class NotFound(DatabaseError):
	"""
	Error for when an object is not found in the database
	"""
	pass

class InvalidDictionary(DatabaseError):
	pass

# Error logging function attached to execute_asynch
def log_errors(errors):
	print errors

# Result printing function attached to execute_asynch
def do_nothing(results):
	print "Written"


# QUERYING APIS

""" TO DO: Set limits on how many results can be returned!!!! 10^6?? """
""" TO DO: Setup some standardized time format (UTC or something?) """

# Function to add a block of time series data
def add_data(sensor_id,event_times,measurements):
	global add_data_insert 
	if add_data_insert == None: 
		add_data_insert = session.prepare("""
			INSERT INTO timestream_by_day
			(sensor_id,date,event_time,measurement)
			VALUES(?,?,?,?);
		""")
	for event_time, measurement in zip(event_times, measurements):
		day = event_time.strftime("%Y%m%d")
		response_future = session.execute_async(bound_statement.bind((
			sensor_id, day, event_time, measurement))
		)
	response_future.add_callbacks(do_nothing, log_errors)

# Function to add a single point of time series data
def add_single_data_pt(sensor_id,event_time,measurement):
	global add_data_pt_insert
	if add_data_pt_insert == None:
		bound_statement = session.prepare("""
			INSERT INTO timestream_by_day
			(sensor_id,date,event_time,measurement)
			VALUES(?,?,?,?);
		""")
	day = event_time.strftime("%Y%m%d")
	response_future = session.execute_async(bound_statement.bind((
		sensor_id, day, event_time, measurement))
	)
	response_future.add_callbacks(do_nothing, log_errors)

# Function to query time series data for a single, whole day
def query_whole_day(sensor_id, day):
	global get_day_query
	if get_day_query is None:
		get_day_query = session.prepare("""
			SELECT event_time, measurement 
			FROM timestream_by_day 
			WHERE sensor_id=? AND date=?;
		""")
	# Execute asynchronousely to avoid errors that I might get here
	future = session.execute_async(get_day_query, (sensor_id,day,))
	handler = PagedResultHandler(future)
	handler.finished_event.wait()
	if handler.error:
		raise handler.error
	# If user is not found, return an error        
	rows = future.result()
	if not rows:
		print('No sensor data for %s on %s' % (sensor_id,day,))
	else:
		print('Sensor data for %s found for %s' % (sensor_id,day,))

	return rows 

def get_timestream_data(sensor_id, start, end):
	""" 
	Given a start/end time and sensor_id, can we find the data they want
	"""
	global get_timestream_query
	if get_timestream_query is None:
		get_timestream_query = session.prepare("""     
		    SELECT event_time, measurement    
		    FROM timestream_by_day                                            
		    WHERE sensor_id=? AND date=?;         
		""")

	# Figure out all the days that we're going to need to pull from start to finish
	no_days = (end-start).days
	start_day = start.date()
	end_day = end.date()

	# In theory, if necessary, I can program a check in here to make sure we're 
	# 1. Not trying to pull days that have no data
	# 2. Not trying to pull days before we've started
	full_days = [start_day+datetime.timedelta(days=i) for i in range(1,no_days+2)]
	for day in full_days:
		results = query_whole_day(sensor_id, day)
		




