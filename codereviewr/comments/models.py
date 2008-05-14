from codereviewr.code.models import Code
from datetime import datetime
from django.contrib.auth.models import User
from akismet import Akismet
from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models

class Comment(models.Model):
    """
    Core comments model for code comments
    """
    name = models.CharField(blank=False,max_length=25)
    email = models.EmailField(blank=False)
    code = models.ForeignKey(Code, related_name='comments')
    lineno = models.IntegerField(blank=True, null=True)
    comment = models.TextField(blank=False, max_length=3000)
    date = models.DateTimeField(default=datetime.now)
    user = models.ForeignKey(User,blank=True,null=True,related_name="comments")
    is_public = models.BooleanField(default=False) #Guilty until proven innocent
    
    def __unicode__(self):
        return "comment on %s by %s" % (self.code.title, self.name)
        
    class Admin:
        list_display = ('name','email', 'code', 'lineno','comment','user','is_public')
    
    class Meta:
        ordering = ('date',)
        
    def _set_spam(self,request):
        if settings.AKISMET:
            akis = Akismet(key=settings.AKISMET_API_KEY, blog_url='http://%s/' % Site.objects.get(pk=settings.SITE_ID).domain)
            if akis.verify_key():
                ak_data = { 
                    'user_ip': request.META.get('REMOTE_ADDR', '127.0.0.1'), 
                    'user_agent': request.META.get('HTTP_USER_AGENT', ''), 
                    'referrer': request.META.get('HTTP_REFERER', ''), 
                    'comment_type': 'comment', 
                    'comment_author': self.name, 
                } 
            if akis.comment_check(self.comment, data=ak_data, build_data=True): 
                self.is_spam = False 
            else: 
                self.is_spam = True    
        else:
            self.is_spam = False
        
    @classmethod
    def submit_spam(cls):
        from pygments.lexers import LEXERS
        languages = [item[1] for item in LEXERS.itervalues()]
        cls.objects.all().delete() # purge all languages
        for l in languages:
            Language(name=l).save() # add language