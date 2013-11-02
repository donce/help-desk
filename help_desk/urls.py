from django.conf.urls import patterns, include, url
from django.contrib import admin

from views import ClientList

admin.autodiscover()

solve_issues_patterns = patterns('help_desk.views',
    url(r'^$', 'solve_issues'),
)

manage_issues_patterns = patterns('help_desk.views',
    url(r'^$', 'manage_issues'),
)

management_patterns = patterns('help_desk.views',
    url(r'^$', 'management_home'),
    url(r'^manage_issues/', include(manage_issues_patterns)),
    url(r'^solve_issues/', include(solve_issues_patterns)),
	url(r'^client', ClientList.as_view()),
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
