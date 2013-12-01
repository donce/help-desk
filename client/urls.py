from django.conf.urls import patterns, url

client_patterns = patterns('client.views',
                           url(r'^$', 'home'),
)
