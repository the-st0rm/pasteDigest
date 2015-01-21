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
<<<<<<< HEAD
    count = pastes = pastebin_log.objects.all().count()
    #pastes = pastebin_log.objects.all().order_by('-datetime', '-wieght')
    amount = 30
    
    paginator = Paginator(pastes, 30)
    r = request.GET
    try:
        p = abs(int(r.get('page', 1)))
    except Exception:
        p=1
    
    start = amount*(p-1)
    if start > amount:
        start=count-amount
    end = start+amount
    no_pages = range(0, count/amount)
    
    keywords = keyword.objects.all()[:3]
    pastes = pastebin_log.objects.all().order_by('-datetime')[start:end]
    pastes = sorted(pastes.all(), key=lambda x:x.wieght, reverse=True)
    c['keywords'] = keywords
    c['pastes'] = pastes
=======
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
>>>>>>> 5b61f7240b2fba7698f14260ab98cf69b5507345
    return render_to_response('main.html', c , context_instance=RequestContext(request) ) 

def get_archive(request):
    requests.get("%s%s" %(WEBSITE, 'archive'))
