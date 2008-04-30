from django.conf.urls.defaults import *
from codereviewr.comments.views import *

urlpatterns = patterns('',
	url(r'^comments/$', comments, name='comments'),
	url(r'^comments/line/(?P<line_no>\d+)$', line_comments, name='line_comments'),
)
