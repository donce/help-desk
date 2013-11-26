from django.conf.urls import patterns, include, url
from django.contrib import admin


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

management_patterns = patterns('help_desk.views',
                               url(r'^$', 'management_home'),
                               url(r'^manage_issues/', include(manage_issues_patterns)),
                               url(r'^solve_issues/', include(solve_issues_patterns)),
                               url(r'^models/', include(models_patterns)),
)

urlpatterns = patterns('',
                       # Examples:
                       url(r'^$', 'help_desk.views.home', name='home'),
                       url(r'^logout/$', 'help_desk.views.logout', name='logout'),
                       url(r'^management/', include(management_patterns)),
                       # url(r'^help_desk/', include('help_desk.foo.urls')),

                       url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
                       url(r'^admin/', include(admin.site.urls)),
)
