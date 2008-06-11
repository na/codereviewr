from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.newforms import ModelForm
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic.list_detail import object_list, object_detail
from codereviewr.code.models import Code, Language, Comment
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_for_filename

#
# FORMS
#

class CodeForm(ModelForm):
    class Meta:
        model = Code
        fields = ('title', 'language', 'code', 'description', 'dependencies', 'version', 'is_public')

class LoggedInCommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('comment',)

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'comment')

#
# VIEWS
#

def code_detail(request, code_id, compare_to_parent=False):
    """
    Displays a single piece of code.
    """
    try:
        code = Code.objects.get(pk=code_id)
    except Code.DoesNotExist:
        raise Http404, "Sorry, the code you requested was not found."
    
    diff_list = Code.objects.filter(parent=code.id)
    
    #get line comments and process into a dictionary of linenumber: number_of_comments pairs for comments flags
    comments = code.comments.filter(lineno__gt=0)
    commentdict= {}
    if comments:
        for comment in comments:
            ln = comment.lineno
            if commentdict.has_key(ln):
                commentdict[ln] += 1 
            else:
                commentdict[ln] = 1

    commentflags = "<table>"
    for i in range(1,code.lncount+1):
        if commentdict.has_key(i):
            number_of_comments = commentdict[i]
            commentflags = commentflags + '<tr><td class="hascomment commentflag">%d</td></tr>' % number_of_comments
        else:
            commentflags = commentflags + '<tr><td class="nocomment commentflag"></td></tr>' 
    commentflags = commentflags + '</table>'
  
    return render_to_response(
        'code/detail.html', {
            'code': code,
            'diff_list': diff_list,
            'commentflags': commentflags,
        },
        context_instance=RequestContext(request)
    )
    
def code_list(request):
    """
    Lists all code flagged as is_public.
    """
    codes = Code.objects.filter(is_public=True)

    if not codes:
        raise Http404, "No code to review, sorry."
    
    return object_list(
        request,
        queryset=codes,
        template_name='code/list.html',
        template_object_name='code',
        paginate_by=50,
    )

@login_required
def code_add(request):
    code = Code()
    if request.method == 'POST':
        form = CodeForm(data=request.POST, instance=code)
        if form.is_valid():
            new_code = form.save(commit=False)
            new_code.author_id = request.user.id
            new_code.save()
            return HttpResponseRedirect(reverse(code_detail, args=(new_code.id,)))
        else:
            pass # Some error
    else:
        form = CodeForm(instance=code)

    return render_to_response(
        'code/add.html',
        {'form': form},
        context_instance=RequestContext(request)
    )

def code_comments(request, code_id,line_no=False):
    """
    Displays comments for a piece of code.
    """
    try:
        code = Code.objects.get(pk=code_id)
    except Code.DoesNotExisit:
        raise Http404, "Sorry, you requested comments for a code that does not exist."
    
    # Initialize comment form with user data if user is authenticated
    data = request.POST.copy()
    if request.user.is_authenticated():
        form = LoggedInCommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.code_id = code_id
            new_comment.lineno = line_no
            if request.user.get_full_name():
                new_comment.name = request.user.get_full_name()
            else:
                new_comment.name = request.user.username
            new_comment.email = request.user.email
            new_comment.user_id = request.user.id
            new_comment.save()
        else:
            pass #some error
    else:
        form = False
        
    if line_no:
        comments = code.comments.filter(lineno=line_no)
    else:
        comments = code.comments.all()
    
    if request.is_ajax():
        return render_to_response(
            'code/comment_list.html', {
                'code':code,
                'comments': comments,
                'form': form,
            },
            context_instance=RequestContext(request)
        )
    else:
        return render_to_response(
            'code/comments.html', {
                'code':code,
                'comments': comments,
                'form': form,                
            },
            context_instance=RequestContext(request)
        )
    
def code_line_comments(request, code_id, line_no):
    """
    Displays line number comments for a piece of code if called by ajax. If not
    redirects to all comments for the piece of code.
    """
    if request.is_ajax():
        try:
            code = Code.objects.get(pk=code_id)
        except Code.DoesNotExisit:
            raise Http404, "Sorry, you requested comments for a code that does not exist."

        return render_to_response(
            'code/comments.html', {
                'code':code,
                'comments': code.comments.all(),
                'form': form,
            },
            context_instance=RequestContext(request)
        )
    
    else:
        return HttpResponseRedirect(reverse(code_comments, args=(code_id,)))

