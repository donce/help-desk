from django.conf.urls import patterns, include, url
from django.contrib import admin

from client.urls import client_patterns


admin.autodiscover()

solve_issues_patterns = patterns('help_desk.views',
                                 url(r'^$', 'solve_issues'),
                                 )

manage_issues_patterns = patterns('help_desk.views',
                                  url(r'^$', 'manage_issues'),
                                  )


models_actions_patterns = patterns('help_desk.views',
                                   url(r'^$', 'model_list'),
                                   url(r'^add/$', 'model_add'),
                                   url(r'^edit/(?P<instance>\d+)/$', 'model_edit'),
                                   url(r'^remove/(?P<instance>\d+)/$', 'model_remove'),
                                   )


models_patterns = patterns('help_desk.views',
                           url(r'^(?P<model>\w+)/', include(models_actions_patterns)),
                           url(r'^$', 'models'),
                           )


administration_patterns = patterns('help_desk.views',
                                   url(r'^$', 'administration'),
                                   url(r'import/$', 'import_database'),
                                   )


management_patterns = patterns('help_desk.views',
                               url(r'^$', 'management_home', {'tab': 'main'}),
                               url(r'^manage_issues/', include(manage_issues_patterns), {'tab': 'manage_issues'}),
                               url(r'^solve_issues/', include(solve_issues_patterns), {'tab': 'solve_issues'}),
                               url(r'^models/', include(models_patterns), {'tab': 'models'}),
                               url(r'^administration/', include(administration_patterns), {'tab': 'administration'}),
                               )


urlpatterns = patterns('',
                       url(r'^$', 'help_desk.views.home', name='home'),
                       url(r'^logout/$', 'help_desk.views.logout', name='logout'),

                       url(r'^service/', include(client_patterns)),
                       url(r'^management/', include(management_patterns)),

                       url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       )
