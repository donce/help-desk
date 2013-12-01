from django.conf.urls import patterns, url

client_patterns = patterns('client.views',
                           url(r'^$', 'home'),
                           url(r'^issues/$', 'issues'),
                           url(r'services/$', 'services'),
                           url(r'contracts/$', 'contracts'),
                           url(r'information/$', 'information'),
)
