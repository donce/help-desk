from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

solve_issues_patterns = patterns('help_desk.views',
    url('^$', 'solve_issues'),
)

manage_issues_patterns = patterns('help_desk.views',
    url('^$', 'manage_issues'),
)

management_patterns = patterns('help_desk.views',
    url('^$', 'management_home'),
    url('^manage_issues/', include(manage_issues_patterns)),
    url('^solve_issues/', include(solve_issues_patterns)),
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
