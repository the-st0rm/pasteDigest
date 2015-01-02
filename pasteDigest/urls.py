from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'pasteDigest.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^home$', 'main.views.main'),
    url(r'^get_archive$', 'main.views.get_archive'),
    
    url(r'^admin/', include(admin.site.urls)),
)
