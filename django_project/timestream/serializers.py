from django.forms import widgets
from rest_framework import serializers
from timestream.models import Snippet, Timestream, SoloTimestream, Device, Sensor, LANGUAGE_CHOICES, STYLE_CHOICES
from django.contrib.auth.models import User

""" Serializer for snippets """
class SnippetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Snippet
        fields = ('id', 'title', 'code', 'language', 'style','sensor',)

""" Serializer for devices """ 
class DeviceSerializer(serializers.ModelSerializer):
	owner = serializers.Field(source='user.username')
	class Meta:
		model = Device
		fields = ('device_id','device_name','location','device_added','user',) 

""" Serializer for sensors """
class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = ('sensor_id','sensor_name','sensor_added','units','device',)

""" Serializer for users """
class UserSerializer(serializers.ModelSerializer):
    devices = serializers.PrimaryKeyRelatedField(many=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'devices')

""" Serializer for timestreams """
class TimeStreamSerializer(serializers.Serializer):
    sensor_id = serializers.CharField()  # <-- seen to override a class here for UUID
    date = serializers.CharField(max_length=8)
    event_time = serializers.DateTimeField()
    measurement = serializers.FloatField()
    
    # Finish this shit
    def restore_object(self, attrs, instance=None):
	""" Given a dictionary of deserialized values, either update an existing model instance
	or create a new model instance """
 	if instance is not None:
	    instance.sensor_id = attrs.get('sensor_id',instance.sensor_id)	
	    instance.date = attrs.get('date',instance.date)	
	    instance.event_time = attrs.get('event_time',instance.event_time)	
	    instance.measurement = attrs.get('measurement',instance.measurement)
	    return instance
	
	return Timestream(**attrs)	


""" Serializer for timestreams """
class SoloTimeStreamSerializer(serializers.Serializer):
    event_time = serializers.DateTimeField()
    measurement = serializers.FloatField()
    
    # Finish this shit
    def restore_object(self, attrs, instance=None):
	""" Given a dictionary of deserialized values, either update an existing model instance
	or create a new model instance """
 	if instance is not None:
	    instance.event_time = attrs.get('event_time',instance.event_time)	
	    instance.measurement = attrs.get('measurement',instance.measurement)
	    return instance
	
	return SoloTimestream(**attrs)	
