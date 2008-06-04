from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.newforms import ModelForm
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic.list_detail import object_list, object_detail
from codereviewr.code.models import Code, Language
from codereviewr.comments.models import Comment
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_for_filename
from codereviewr.code.util import *
#
# FORMS
#

class CodeForm(ModelForm):
	class Meta:
		model = Code
		fields = ('title', 'code', 'description', 'dependencies', 'version', 'is_public')

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
	code.highlight = ""
	# Pygmentize code
	lexer = get_lexer_for_filename('test.py', stripall=True)
	formatter = CodereviewerHtmlFormatter(linenos=True, cssclass="source", lineanchors="line") 
	code.highlight = highlight(code.code, lexer, formatter)
	
	#compare to parent
	if compare_to_parent:
		lexer = get_lexer_for_filename('test.diff')
		formatter = DiffHtmlFormatter(cssclass="source") #carefull css options might break the regular expressions
		code.highlight = highlight(code.compare_to_parent(), lexer, formatter)
		
	return render_to_response(
		'code/detail.html',
		{'code': code,
		'diff_list':diff_list,
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
		
def refresh_languages(request):
	Language.load_languages()
	return HttpResponseRedirect('/admin/code/language/')