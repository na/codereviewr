from codereviewr.code.models import Code
from codereviewr.comments.models import Comment
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.newforms import ModelForm
from django.shortcuts import render_to_response
from django.template import RequestContext
#
# FORMS
#
class LoggedInCommentForm(ModelForm):
	class Meta:
		model = Comment
		fields = ('comment')

class CommentForm(ModelForm):
	class Meta:
		model = Comment
		fields = ('name', 'email', 'comment')

#
# FORMS
# 

def comments(request, code_id):
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
			if request.user.get_full_name():
				new_comment.author = request.user.get_full_name()
			else:
				new_comment.author = request.user.username
			new_comment.email = request.user.email
			new_comment.user_id = request.user.id
			new_comment.save()
		else:
			pass #some error
	else:
		form = CommentForm(request.POST)
		
	return render_to_response(
		'comments/comments.html',
		{'code':code,
		'comments': code.comments.all(),
		'form':form,
		},
		context_instance=RequestContext(request)
	)
	
def line_comments(request, code_id, line_no):
	"""
	Displays line number comments for a piece of code if called by ajax. If not redirects to all comments for the piece of code.
	"""
	# Initialize comment form with user data if user is authenticated
	data = request.POST.copy()
	if request.user.is_authenticated():
		form = LoggedInCommentForm(request.POST)
		if form.is_valid():
			new_comment = form.save(commit=False)
			new_comment.code_id = code_id
			if request.user.get_full_name():
				new_comment.author = request.user.get_full_name()
			else:
				new_comment.author = request.user.username
			new_comment.email = request.user.email
			new_comment.user_id = request.user.id
			new_comment.save()
		else:
			pass #some error
	else:
		form = CommentForm(request.POST)
	
	if request.is_ajax():
		try:
			code = Code.objects.get(pk=code_id)
		except Code.DoesNotExisit:
			raise Http404, "Sorry, you requested comments for a code that does not exist."
		
		return render_to_response(
			'comments/jax_comments.html',
			{'code': code,
			'comments': code.comments.filter(lineno=line_no),
			'form': form,
			'line_no': line_no,
			},
			context_instance=RequestContext(request)
		)
	else:
		return HttpResponseRedirect(reverse(code_comments, args =(code_id,)))