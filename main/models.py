from django.db import models

WEBSITE ='http://www.pastebin.com'

class pastebin_log(models.Model):
    datetime= models.DateTimeField()
    title   = models.CharField(max_length=255)
    url     = models.CharField(max_length=255)
    syntax  = models.CharField(max_length=255)
    content = models.TextField()
    visitors= models.IntegerField()
    

    def __str__(self):
        return "%s: %s" %(self.url, self.title)
    
    def get_url(self):
        return "%s/%s" %(WEBSITE, self.url)
    