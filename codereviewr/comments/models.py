from codereviewr.code.models import Code
from datetime import datetime
from django.contrib.auth.models import User
from django.db import models

class Comment(models.Model):
    """
    Core comments model for code comments
    """
    author = models.CharField(blank=False,max_length=25)
    email = models.EmailField(blank=False)
    code = models.ForeignKey(Code, related_name='comments')
    lineno = models.IntegerField(blank=True, null=True)
    comment = models.TextField(blank=False)
    date = models.DateTimeField(default=datetime.now)
    user = models.ForeignKey(User,blank=True,null=True,related_name="comments")
    
    def __unicode__(self):
        return "comment on %s by %s" % (self.code.title, self.author)
        
    class Admin:
        list_display = ('author','email', 'code', 'lineno','comment','user')
    
    class Meta:
        ordering = ('date',)