from django.db import models

WEBSITE ='http://www.pastebin.com'

class pastebin_log(models.Model):
    datetime= models.DateTimeField()
    title   = models.CharField(max_length=255)
    url     = models.CharField(max_length=255)
    syntax  = models.CharField(max_length=255)
    content = models.TextField()
    wieght = models.IntegerField(default=0)
    visitors= models.IntegerField()
    

    def __str__(self):
        return "%s: %s" %(self.url, self.title)
    
    def get_url(self):
        return "%s/%s" %(WEBSITE, self.url)

class keyword(models.Model):
    name = models.CharField(max_length=255)
    weight = models.IntegerField(default=5)
    reps = models.IntegerField(default=0)
    paste_posts = models.ManyToManyField(pastebin_log)

    def __str__(self):
        return self.name
    
    