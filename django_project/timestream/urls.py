from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns
from timestream import views

urlpatterns = patterns('',
	# Get everything or post to add one
    url(r'^snippets/$', views.SnippetList.as_view()),
    url(r'^devices/$', views.DeviceList.as_view()),
    url(r'^sensors/$', views.SensorList.as_view()),
    # Individual look for snipper, sensor, device
	url(r'^snippets/(?P<pk>[0-9]+)/$', views.SnippetDetail.as_view()),
    url(r'^sensors/(?P<pk>[0-9]+)/$', views.SnippetDetail.as_view()),
    url(r'^devices/(?P<pk>[0-9]+)/$', views.SnippetDetail.as_view()),
	# Timestream look to for a single day
	url(r'^timestream/$', views.timestream, name='timestream'),
	url(r'^timestream/(?P<uuid>[^/]+)/$',views.timestream_sensor, name='timestream_sensor'),
	# User look - shows user info and links to user devices
	url(r'^users/$', views.UserList.as_view()),
	url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view()),

	# Rest framework api authentication
	url(r'^api-auth/', include('rest_framework.urls',namespace='rest_framework')),

)

urlpatterns = format_suffix_patterns(urlpatterns)
