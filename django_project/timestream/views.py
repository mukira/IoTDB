from timestream.models import Snippet, Device, Sensor, Timestream, SoloTimestream
from timestream.serializers import SnippetSerializer, DeviceSerializer, SensorSerializer, TimeStreamSerializer, SoloTimeStreamSerializer, UserSerializer
from rest_framework import generics, permissions
from timestream.permissions import IsOwnerOrReadOnly
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
import cass   # our python functions interacting with cassandra
import datetime
from django.contrib.auth.models import User

""" Return the entire serialized user list or accept posts to it """
class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

""" Return the specifics of a given user, allow view, edit, and delete """
class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

""" Return the entire serialized snippet list or accept posts to it """
class SnippetList(generics.ListCreateAPIView):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer

""" Return the specifics of a given snippet, allow view, edit, and delete """
class SnippetDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer

""" Return the entire serialized device list and accept posts to it """
class DeviceList(generics.ListCreateAPIView):
	queryset = Device.objects.all()
	serializer_class = DeviceSerializer
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly)
	def pre_save(self, obj):
		obj.owner = self.request.user

""" Return the specifics of a given device, allow view, edit, and delete """
class DeviceDetail(generics.RetrieveUpdateDestroyAPIView):
	queryset = Device.objects.all()
	serializer_class = DeviceSerializer
	permission_classes = (permissions.IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly)    
	def pre_save(self, obj):
		obj.owner = self.request.user

""" Return the entire serialized sensor list and accept posts to it """
class SensorList(generics.ListCreateAPIView):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer

""" Return the specifics of a given sensor, allow view, edit, and delete """
class SensorDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer

""" First attempt to play with the rest API + Cassandra """
@csrf_exempt  # Note: For security reasons, this is not the best way to do this...its just for now!
@api_view(['GET','POST'])
def timestream(request):
	sensor_id = '63a97551-9973-4ccb-8db8-20a04f51203b'
	day = '20140101'
	results = cass.query_whole_day(sensor_id, day)	
	if request.method == 'GET':
		# get our collection of timestream stuff for this day
		#timestreams = []	
		#df = pd.DataFrame(results)
		#df.set_index(0)
		timestreams = [SoloTimestream(r[0],r[1]) for r in results[:10]]
		serializedList = SoloTimeStreamSerializer(timestreams, many=True)
		return Response(serializedList.data)
	elif request.method == 'POST':
		# Why is this throwing me a weird error here!?
		sensor_id = request.POST["sensor_id"]
		event_time = request.POST["event_time"]
		measurement = request.POST["measurement"]
		return Response({"ok": "true" })
		try:
			cass.add_single_data_pt(sensor_id, event_time, measurement)
			return Response({"ok": "true" })
		except: 
			return Response({"ok": "false" })
