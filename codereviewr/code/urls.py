from django.conf.urls.defaults import *
from codereviewr.code.views import *

urlpatterns = patterns('',
    url(r'^$', code_list, name='code_list'),
    url(r'^add/$', code_add, name='code_add'),
    url(r'^(?P<code_id>\d+)/$', code_detail, name='code_detail'),
    url(r'^(?P<code_id>\d+)/(?P<compare_to_parent>diff)/$', code_detail, name='code_diff'),
    url(r'^(?P<code_id>\d+)/comments/$', code_comments, name='code_comments'),
    url(r'^(?P<code_id>\d+)/comments/line/(?P<line_no>\d+)$', code_comments, name='code_line_comments'),
)
