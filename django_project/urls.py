from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
                       
    # Include everything from this folder without any web prefix
    url(r'^$', 'views.home', name='home'),

    url(r'^auth/login/$',  login, name='login'),
    url(r'^auth/logout/$', logout, name='logout'),

    # Include all the timestream urls as well
    url(r'^timestream/', include('timestream.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

