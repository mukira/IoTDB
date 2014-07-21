from django.db import models
from django.contrib.auth.models import User
from uuid import uuid4

import time
import datetime
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles

LEXERS = [item for item in get_all_lexers() if item[1]]
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])
STYLE_CHOICES = sorted((item, item) for item in get_all_styles())

""" Simple Device Class"""
class Device(models.Model):
    device_name = models.CharField(max_length=30)
    location = models.CharField(verbose_name="Location of Device", max_length=100, blank=True, default='')
    device_added = models.DateField(verbose_name="Date of Device Activation", auto_now_add=True)
    device_id = models.CharField(verbose_name="Device Unique Identifier", default=uuid4().hex, primary_key=True, max_length=32)
    user = models.ManyToManyField(User, verbose_name="Associated Users",related_name='devices')

    def __str__(self):
        return self.device_name

    class Meta:
        ordering = ('device_name', 'device_added',)


""" Simple Sensor Class """
class Sensor(models.Model):
    sensor_name = models.CharField(max_length=30)
    sensor_id = models.CharField(verbose_name="Sensor Unique Identifer", default=uuid4().hex, primary_key=True,max_length=32)
    sensor_added = models.DateField(verbose_name="Sensor Activiation Date", auto_now_add=True)
    units = models.CharField(verbose_name="Measurement Units", max_length=30,blank=True,default='')
    device = models.ForeignKey(Device,verbose_name="Associated Device")

    def __str__(self):
        return self.sensor_name

    class Meta:
        ordering = ('sensor_name','sensor_added',)


""" Simple code snippet model """
class Snippet(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=True, default='')
    code = models.TextField()
    language = models.CharField(choices=LANGUAGE_CHOICES,
                                default='python',
                                max_length=100)
    style = models.CharField(choices=STYLE_CHOICES,
                             default='friendly',
                             max_length=100)
    sensor = models.ManyToManyField(Sensor,verbose_name="Associated Sensors")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('created',)


""" Some simple code for adding to cassandra database by inputting all params """
class Timestream(object):
    def __init__(self, sid, stime, value):
		self.sensor_id = sid
		self.event_time = stime
		self.date = stime.strftime("%Y%m%d")
		self.measurement = value


""" Some simple code for adding to cassandra database by specifying only datetime and measurement """
class SoloTimestream(object):
    def __init__(self, stime, value):
		self.event_time = stime
		self.measurement = value
