from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.template import Context
import BeautifulSoup
from main.models import *
import requests
# Create your views here.



WEBSITE = "http://www.pastebin.com/"
def main(request):
    c = dict()
    pastes = pastebin_log.objects.all().order_by('-datetime')[:30]
    c['pastes'] = pastes
    return render_to_response('main.html', c , context_instance=RequestContext(request) ) 

def get_archive(request):
    requests.get("%s%s" %(WEBSITE, 'archive'))
    
