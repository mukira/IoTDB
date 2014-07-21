# -*- coding: utf-8 -*-
''' 
Tutorial for setting up Apache Cassandra using Datastax's Python Drivers

'''

# Do the import thing
from cassandra.cluster import Cluster
import time
# Import logging with configuration
import logging
# Import the uuid function 
from uuid import uuid1, UUID
import pandas as pd
import numpy as np
from datetime import datetime


logging.basicConfig()

# Instantiate the Log
log = logging.getLogger()
log.setLevel('INFO')

# Error logging function attached to execute_asynch
def log_errors(errors):
    log.error(errors)

# Result printing function attached to execute_asynch
def print_results(results):
    print "%-30s\t%-20s\t%-20s%-30s\n%s" % \
        ("title", "album", "artist", "tags", 
        "-------------------------------+-----------------------+--------------------+-------------------------------")
    for row in results:
        print "%-30s\t%-20s\t%-20s%-30s" % (row.title, row.album, row.artist, row.tags)
        

# Class to create the a simple client object for cassandra
class SimpleClient:
    session = None
    
    # Function to drop a schema from storage
    def drop_schema(self, keyspace):
        log.info("dropping keyspace %s" % keyspace)
        self.session.execute("DROP KEYSPACE " + keyspace)

    
    # Build cluster, retrieve metadata, connect to cluster, print results
    def connect(self, nodes):
        # Load this Cluster
        cluster = Cluster(nodes)
        # Grab the metadata for it
        metadata = cluster.metadata
        # Connect to the cluster
        self.session = cluster.connect()
        # Print cluster name 
        log.info('Connected to cluster: ' + metadata.cluster_name)
        for host in metadata.all_hosts():
            # Print individual host information
            log.info('Datacenter: %s; Host: %s; Rack: %s',
                     host.datacenter, host.address, host.rack)
                     
    # Shut down the cluster object when finished with it
    def close(self):
        # Shut down the cluster
        self.session.cluster.shutdown()
        # Shut down the session
        self.session.shutdown()
        # Write out the result
        log.info('Connection closed.')
        
    # Create a database schema
    def create_schema(self):

        # Create a new keyspace, simplex1, with a 3x replication of data
        self.session.execute(""" 
             CREATE KEYSPACE IoTDB WITH replication
             = {'class':'SimpleStrategy', 'replication_factor':3};
             """)

        # Create a table to house the user info 
        self.session.execute(""" 
             CREATE TABLE IoTDB.users (
                 username text PRIMARY KEY,
                 password text,
             );
        """)

        # Create a table to house the device info by device_id - a pull gives all the info for a particular device (ie - which users can see it)
        self.session.execute(""" 
             CREATE TABLE IoTDB.devices (
                 device_id uuid,
                 device_name text,
                 device_loc text,
                 username text,
                 PRIMARY KEY (username,device_id)
             );
        """)
        
        # Create a table to house the sensor info by user - for a given user, just pull all their sensors
        self.session.execute("""
             CREATE TABLE IoTDB.sensors (
                 username text,
                 sensor_id uuid,
                 sensor_name text,
                 device_id uuid, 
                 device_name text,
                 units text,
                 PRIMARY KEY (username, sensor_id)
             );
        """)        

        # Create a table to house the timstream info keyed by user, 
        self.session.execute("""
             CREATE TABLE IoTDB.timestream_by_day(
                 sensor_id uuid,
                 device_id uuid, 
                 username text,
                 date text,
                 event_time timestamp, 
                 measurement double,
                 PRIMARY KEY ((username, device_id, sensor_id, date), event_time),
             )
             WITH CLUSTERING ORDER BY (event_time DESC);
        """)    

        # Log database creation
        log.info('IoTDB keyspace and table schema created.')
    
    # Method to query the DB and return all users
    def query_all_users(self):

        get_usernames_query = self.session.prepare("""
            SELECT * FROM iotdb.users
        """)

        # Perform the query
        rows = self.session.execute(get_usernames_query)
        # If user is not found, return an error
        if not rows:
            print('No users found')
        # If user is found, return the user, only first one cause usernames are unique in theory
        else:
            log.info('%s users in database' % (str(len(rows,))))
            return rows
        

    # Function to query users by a single username, return user if found
    def query_users(self,username):
        
        get_usernames_query = self.session.prepare("""
            SELECT * FROM iotdb.users WHERE username=?
        """)

        # Perform the query
        rows = self.session.execute(get_usernames_query, (username,))
        # If user is not found, return an error
        if not rows:
            print('User %s not found' % (username,))
        # If user is found, return the user, only first one cause usernames are unique in theory
        else:
            log.info('User schema queried for username %s' % (username,))
            return rows[0]

    
    # Function to query all devices for a given user
    def query_devices(self,username):

        get_devices_query = self.session.prepare("""
            SELECT * FROM iotdb.devices WHERE username=?
        """)
        rows = self.session.execute(get_devices_query, (username,))
        if not rows:
            print('No devices found for username %s' % (username,))
        else:
            results = [row for row in rows]
            log.info('%s devices found for username %s' % (str(len(results)),username,))
            return results


    # Function to query all devices for a given user
    def query_all_devices(self):

        get_devices_query = self.session.prepare("""
            SELECT * FROM iotdb.devices 
        """)
        rows = self.session.execute(get_devices_query)
        #rows = self.session.execute(get_devices_query)
        if not rows:
            print('No devices found')
        else:
            log.info('%s devices found' % (str(len(rows)),))
            return rows #[row.device_id for row in rows]


    # Function to query for all sensors of a given user
    def query_sensors(self,uname):
        get_sensor_query = self.session.prepare("""
            SELECT * FROM iotdb.sensors WHERE username=?
        """)
        rows = self.session.execute(get_sensor_query, (uname,))
        if not rows:
            print('No sensors found for user %s' % (uname,))
        else:
            results = [row for row in rows]
            log.info('%s matching sensors found' % (str(len(results)),))
            return results


    # Bound statement function to add user - change input usernames and pwds
    def add_users(self, usernames, pwds):
        # Prepare an insert statement - prepare makes this a bound statement
        bound_statement = self.session.prepare("""
            INSERT INTO iotdb.users
            (username, password)
            VALUES (?, ?);
        """)
        # Now insert some user data
        for u,p in zip(usernames, pwds):
            self.session.execute(bound_statement.bind((
                u,p))
            )


    # Function to add a devices - change for input info
    def add_devices(self, names, locs, unames):

        # Add bound statement for devices function
        bound_statement1 = self.session.prepare("""
            INSERT INTO iotdb.devices
            (device_id,device_name,device_loc,username)
            VALUES (?, ?, ?, ?);
        """)
        
        for name, loc, uname in zip(names, locs, unames):
            this_uuid = uuid1()
            self.session.execute_async(bound_statement1.bind((
                this_uuid, name, loc, uname))
            )

    
    # Function to add a devices - change for input info
    def add_sensors(self, sensor_names, device_ids, device_names, usernames, units):

        # Add bound statement for sensors function
        bound_statement = self.session.prepare("""
            INSERT INTO iotdb.sensors
            (username,sensor_id,sensor_name,device_id,device_name,units)
            VALUES (?, ?, ?, ?, ?, ?);
        """)
        # And execute it
        for sensor_name,device_id,device_name,username,unit in zip(sensor_names,device_ids,device_names,usernames,units):
            this_uuid = uuid1()
            self.session.execute(bound_statement.bind((
                username,this_uuid,sensor_name,device_id,device_name,unit))
            )
            
    # Function to add time series data
    def add_data(self,sensor_id,device_id,username,dates,event_times,measurements):
        bound_statement = self.session.prepare("""
            INSERT INTO iotdb.timestream_by_day
            (sensor_id,device_id,username,date,event_time,measurement)
            VALUES(?,?,?,?,?,?);
        """)
        #VALUES (’1234ABCD’,’2013-04-03′,’2013-04-03 07:02:00′,’73F’);
        for d, event_time, measurement in zip(dates, event_times, measurements):
            dtime = datetime.strptime(event_time, "%Y-%m-%d %H:%M:%S")
            self.session.execute(bound_statement.bind((
                sensor_id, device_id, username, d, dtime, measurement))
            )
        

# Execute functions block calling threads until they finish execting. To avoid this, run asynchronously as below
class AsynchronousExample(SimpleClient):
    
    # Function override for query_schema
    def query_schema(self):
        # Use execute_asynch instead of execute
        response_future = self.session.execute_async("SELECT * FROM simplex1.songs;")
        # Add two callback functions to response_future
        response_future.add_callbacks(print_results, log_errors)
    
        
# Function to pull the stocks into the database
def pull_stocks(locations):
    # Load some devices
    import os
    path_to_files = "/home/smoyerman"
    names = []
    locs = []
    for loc in locations:
        files = [x for x in os.listdir(path_to_files+'/'+loc) if '.txt' in x]
        n = []
        for f in files:
            a,b,c = f.split('.')
            n.append(a) 
        names.extend(n)
        locs.extend([loc]*len(n))
    return names, locs
	
                
# Module main function        
def main():
    
    # Create the client object
    client = SimpleClient()
    
    # Connect the client object to local host
    client.connect(['127.0.0.1'])
    client.drop_schema("IoTDB")
    
    # Create the keyspace and table schema
    client.create_schema()
    
    # Load some users
    usernames = ["smoyerman","jsendowski"]
    pwds = ["judo2039","jsendowski"]
    client.add_users(usernames, pwds)   # Add us to the DB
    unames = client.query_all_users()   # Query us from the DB
    
    # Data locations on the drive
    #locations = ["nyse","nasdaq","nysemkt"]
    locations = ["nyse"]
    names, locs = pull_stocks(locations)
    # Add the stocks to Jacob
    unames1 = [unames[1].username]*len(names)
    client.add_devices(names, locs, unames1)   # 3360 NYSE devices for Jacob
    
    # Query my devices as a spot check
    devices = client.query_devices(unames[1].username)
    # Add the sensors based on the device data - Date,Time,Open,High,Low,Close,Volume,OpenInt
    sensors = ['Open','High','Low','Close','Volume','OpenInt']
    units = ['USD','USD','USD','USD','M','Bin']
    device_ids = [device.device_id for device in devices]
    device_names = [device.device_name for device in devices]
    for sensor,unit in zip(sensors,units):
        print sensor
        sensor_names = [sensor]*len(device_ids)
        unts = [unit]*len(device_ids)    
        usernames = [unames[1].username]*len(device_ids)
        client.add_sensors(sensor_names, device_ids, device_names, usernames, unts)
    # Check that this worked
    input_sensors = client.query_sensors(unames[1].username)    # 20160 sensors for Jacob
    
       
    # Now we need to load the data
    path_to_data = "/home/smoyerman"
    file_paths = [path_to_data + '/nyse/' + input_sensor.device_name + '.us.txt' for input_sensor in input_sensors]
    sensor_ids = [input_sensor.sensor_id for input_sensor in input_sensors]
    device_ids = [input_sensor.device_id for input_sensor in input_sensors]
    sensor_names = [input_sensor.sensor_name for input_sensor in input_sensors]
    for f,s_id,d_id,s_name in zip(file_paths,sensor_ids,device_ids,sensor_names):
        try:
            data = pd.read_csv(f)
            data['DateTime'] = data['Date'] + ' ' + data['Time']
            client.add_data(s_id,d_id,unames[1].username,data['Time'],list(data['DateTime']),list(data[s_name]))
            print f
        except:
            continue 
            
    client.close()


# Run the thing for fuck's sake
if __name__ == "__main__":
    main()
