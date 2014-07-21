from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect

# Create your views here.
def home(request):
    context = {'current_date':''}
    return render_to_response('index.html', context, context_instance=RequestContext(request))
