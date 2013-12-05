from django.conf.urls import patterns, url

client_patterns = patterns('client.views',
                           url(r'^$', 'home'),
                           url(r'^issues/$', 'issues', {'tab': 'issues'}),
                           url(r'services/$', 'services', {'tab': 'services'}),
                           url(r'contracts/$', 'contracts', {'tab': 'contracts'}),
                           url(r'information/$', 'information', {'tab': 'information'}),
)
