from django.conf.urls import patterns, include, url
from django.contrib import admin

from client.urls import client_patterns
from help_desk.urls import management_patterns


admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^$', 'help_desk.views.home', name='home'),
                       url(r'^logout/$', 'help_desk.views.logout', name='logout'),
                       url(r'^change_language/$', 'common.views.set_language'),

                       url(r'^service/', include(client_patterns)),
                       url(r'^management/', include(management_patterns)),

                       url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^i18n/', include('django.conf.urls.i18n')),
                       )
