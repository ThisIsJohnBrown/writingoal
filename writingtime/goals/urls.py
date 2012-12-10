from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('writingtime.goals.views',
    url(r'^create/$', 'goal_create', name='goal_create'),
    url(r'^html/$', 'goal_html', name='goal_html'),
    url(r'^entry/$', 'entry_create', name='entry_create'),

    #url(r'^social/created/$', 'social_created', name='connections_social_created'),
    #url(r'^send/(?P<id>\w+)/$', 'send', name='connections_send'),
    #url(r'^accept/(?P<id>\w+)/$', 'accept', name='connections_accept'),
    #url(r'^reject/(?P<id>\w+)/$', 'reject', name='connections_reject'),
    #url(r'^', 'index', name='connections_index'),
)
