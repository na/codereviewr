from difflib import unified_diff
from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from datetime import datetime
from pygments import formatters, highlight, lexers

import StringIO
import re

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
            self.Formatter(linenos='table', lineanchors='line')
        )
        super(Code, self).save()
        
    class Meta:
        verbose_name_plural = 'code'
 
    class Admin:
        list_display = ('title','author','is_public','created')

    class Formatter(formatters.HtmlFormatter):
        def wrap(self, source, outfile):
            return self._wrap_code(source)

        def _wrap_code(self, source):
            j=1
            yield 0, '<pre><table>'
            for i, t in source:
                if i == 1:
                    b = '<tr class="line-%d"><td>' % j
                    e = '</td></tr>'
                    t = b+t+e
                    # it's a line of formatted code
                    yield i, t
                    j += 1
            yield 0, '</table></pre>'

        """override to include anchor tags around the line numbers"""
        def _wrap_tablelinenos(self, inner):
            dummyoutfile = StringIO.StringIO()
            lncount = 0
            for t, line in inner:
                if t:
                    lncount += 1
                dummyoutfile.write(line)
            fl = self.linenostart
            mw = len(str(lncount + fl - 1))
            sp = self.linenospecial
            st = self.linenostep
            la = self.lineanchors
            if sp:
                ls = '\n'.join([(i%st == 0 and
                                 (i%sp == 0 and '<a href=#%s-%d class="special">%*d</a>'
                                  or '<a href=#%s-%d>%*d</a>') % (la, i, mw, i)
                                 or '')
                                for i in range(fl, fl + lncount)])
            else:
                """ls = '\n'.join([(i%st == 0 and ('<a href=#%s-%d>%*d</a>' % (la, i, mw, i)) or '') # added </a><a href=#>
                                for i in range(fl, fl + lncount)])
                """
                ls = ''
                linecomments = ''
                for i in range (fl, fl+ lncount):
                    comments = Comment.objects.filter(lineno=i)
                    if comments.count() > 0:
                        ls = ls + '<tr><td class="lineno line-%d"><div class="commentflag hascomment">%d</div><a href=#%s-%d>%d</a></td></tr>' % (i,comments.count(),la,i,i)
                    else:
                        ls = ls + '<tr><td class="lineno line-%d"><div class="commentflag nocomment"></div><a href=#%s-%d>%d</a></td></tr>' % (i,la,i,i)

            yield 0, ('<table class="%stable">' % self.cssclass +
                      '<tr><td class="linenos"><pre><table>' +
                      ls + '</table></pre></td><td class="code">')
            yield 0, dummyoutfile.getvalue()
            yield 0, '</td></tr></table>'

class Comment(models.Model):
    """
    Core comments model for code comments
    """
    name = models.CharField(blank=False, max_length=100)
    email = models.EmailField(blank=False)
    code = models.ForeignKey(Code, related_name='comments')
    lineno = models.IntegerField(blank=True, null=True)
    comment = models.TextField(blank=False)
    date = models.DateTimeField(default=datetime.now)
    user = models.ForeignKey(User, blank=True, null=True, related_name="comments")

    def __unicode__(self):
        return "comment on %s by %s" % (self.code.title, self.name)
    class Admin:
        list_display = ('name','email', 'code', 'lineno','comment','user')
    
    class Meta:
        ordering = ('date',)
