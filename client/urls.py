from django.conf.urls import patterns, url, include

issues_patterns = patterns('client.views',
                           url(r'^$', 'issues'),
                           url(r'^create/$', 'create_issue'),
                           url(r'^edit/(?P<issue_id>\d+)/$', 'edit_issue'),
                           )

client_patterns = patterns('client.views',
                           url(r'^$', 'home'),
                           url(r'^issues/', include(issues_patterns), {'tab': 'issues'}),
                           url(r'^services/$', 'services', {'tab': 'services'}),
                           url(r'^contracts/$', 'contracts', {'tab': 'contracts'}),
                           url(r'^information/$', 'information', {'tab': 'information'}),
                           )
