﻿from django.conf.urls.defaults import *
from django.contrib.comments.feeds import LatestCommentsFeed
from django.views.generic.simple import direct_to_template, redirect_to
from codereviewr.settings import PROJECT_PATH, DEBUG
from codereviewr.feeds import *

#feeds dictionary
feeds = {
    'code': CodeFeed,
    'comments': LatestCommentsFeed,
    'language': LanguageFeed,
    'latest': LatestFeed,
    'user': UserFeed,
}

urlpatterns = patterns('',
    (r'^code/', include('codereviewr.code.urls')),
    
    # Admin
    (r'^admin/', include('django.contrib.admin.urls')),

    # account registration
    #(r'^accounts/', include('registration.urls')),
    (r'^accounts/', include('authopenid.urls')),

    #for homepage - testing
    (r'^$', direct_to_template, {'template': 'homepage.html'}),
    
    #Feeds
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
)

if DEBUG:
    urlpatterns += patterns('', 
        (r'^media/(.*)$', 'django.views.static.serve', {'document_root': '%s/../media' % (PROJECT_PATH)})
    )
