from django.conf.urls.defaults import *
from codereviewr.code.views import *

urlpatterns = patterns('',
	url(r'^comments/$', code_comments, name='code_comments'),
	url(r'^comments/line/(?P<line_no>\d+)$', code_line_comments, name='code_line_comments'),
)
