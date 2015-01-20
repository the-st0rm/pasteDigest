from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.template import Context
from main.models import *
import requests
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.




#adding pagination
WEBSITE = "http://www.pastebin.com/"
def main(request):
    c = dict()
    pastes = pastebin_log.objects.all().order_by('-datetime')
    paginator = Paginator(pastes, 30)
    r = request.GET
    p = r.get('page', 1)
    try:
        res = paginator.page(p)
    except PageNotAnInteger:
        res = paginator.page(1)
    except EmptyPage:
        res = paginator.page(paginator.num_pages)
    c['pastes'] = res
    return render_to_response('main.html', c , context_instance=RequestContext(request) ) 

def get_archive(request):
    requests.get("%s%s" %(WEBSITE, 'archive'))
    
