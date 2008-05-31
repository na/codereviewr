from difflib import unified_diff
from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from datetime import datetime
from pygments import formatters, highlight, lexers

class Language(models.Model):
    """
    Lookup table for languages
    To create these in the admin, see http://pygments.org/docs/lexers/
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(prepopulate_from=('name',))
    lexer_name = models.CharField(max_length=100, help_text="The name given to Pygment's get_lexer_by_name method.")
    file_extension = models.CharField(max_length=10, blank=True, help_text="The file extensions for downloads.  No dot.")
    mime_type = models.CharField(max_length=100, help_text="The HTTP content-type to use for downloads.")
    
    class Admin:
        list_display = ('name', 'slug', 'file_extension', 'mime_type')
        ordering = ('name',)
 
    def __unicode__(self):
        return self.name

    def get_lexer(self):
        """Returns a Pygments Lexer object using lexer_name"""
        return lexers.get_lexer_by_name(self.lexer_name)

class Code(models.Model):
    """
    Core code model for code snippets
    """
    title = models.CharField(max_length=200)
    code = models.TextField()
    code_html = models.TextField(editable=False)
    author = models.ForeignKey(User)
    description = models.TextField(blank=True)
    dependencies = models.CharField(blank=True, max_length=255)
    language = models.ForeignKey(Language, db_index=True)
    version = models.CharField(blank=True, max_length=100)
    is_public = models.BooleanField(default=True)
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(blank=True, default=datetime.now)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='child_set')
    
    def __unicode__(self):
        return "%s by %s" % (self.title, self.author.get_full_name())
    
    def compare_to_parent(self, lines=3):
        #diff = Differ()
        #comp = list(diff.compare(code.parent.code.split('\n'),code.code.split('\n')))
        comp = list(unified_diff(self.parent.code.split('\n'),self.code.split('\n'),'orig.','sugg.',n=lines))
        return ''.join(comp)

    def get_absolute_url(self):
        return ('code_detail', [str(self.id)])
    get_absolute_url = models.permalink(get_absolute_url)

    def save(self):
        self.updated = datetime.now()
        self.code_html = highlight(
            self.code,
            self.language.get_lexer(),
            formatters.HtmlFormatter(linenos=True)
        )
        super(Code, self).save()
        
    class Meta:
        verbose_name_plural = 'code'
 
    class Admin:
        list_display = ('title','author','is_public','created')
 
class Comment(models.Model):
    """
    Core comments model for code comments
    """
    author = models.CharField(blank=False, max_length=100)
    email = models.EmailField(blank=False)
    code = models.ForeignKey(Code, related_name='comments')
    lineno = models.IntegerField(blank=True, null=True)
    comment = models.TextField(blank=False)
    date = models.DateTimeField(default=datetime.now)
    user = models.ForeignKey(User, blank=True, null=True, related_name="comments")
    
    """
    def save(self):
        user = User.objects.filter(username=self.author,email=self.email) 
        
        if user.count()==1: 
            self.author_is_user = True
        super(Comment,self).save()
    """
    def __unicode__(self):
        return "comment on %s by %s" % (self.code.title, self.author)
        
    class Admin:
        list_display = ('author','email', 'code', 'lineno','comment','user')
    
    class Meta:
        ordering = ('date',)
