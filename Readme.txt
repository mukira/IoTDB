Welcome to the IoTDB readme file!

A little overview

IoTDB is a cloud database service optimized for timeseries storage across multiple devices. It is designed to scale to millions of devices with multiple corresponding sensors across millions or more users. The timeseries aspect sotres data down to the microsecond resolution.

Overview:
(1) The web server is Django, mainly because of the extensive ongoing development, excellent documentation, and wide range of extendable packages 
(2) The database for users + devices + sensors + code is dont in PostGRESQL. There are a few reasons for this: the data is inherently related and lends itself well to an RDBMS, Django works extremely well with PostGREs, auth procedures come naturally from the framework, etc. 
(3) The database for timeseries uses the noSQL database Cassandra with the datastax python drivers to communicate in django.
(4) The REST API is developed using the Django REST Framework, chosen mainly for the same reasons that django was chosen. 

Outlying tasks:
(1) Finish REST API for push to time series and cassandra
(2) Develop and code a set of test scripts to push data to the rest framework and evaluate the results (eval done on command line)
(3) Install blueflood from rackspace for automatic roll ups in another cassandra database
(4) Use memcached for django to handle caching in a reasonable way
(5) Scale out to multiple nodes for cassandra, blueflood, and django. Test the speed and aptitude of this thing. 
