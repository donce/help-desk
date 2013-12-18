from django.conf.urls import patterns, url, include

solve_issues_patterns = patterns('help_desk.views',
                                 url(r'^$', 'solve_issues'),
                                 url(r'^view_issue/(?P<issue>\d+)/$', 'view_issue'),
                                 )

manage_issues_patterns = patterns('help_desk.views',
                                  url(r'^$', 'manage_issues'),
                                  url(r'^edit_issue/(?P<issue_id>\d+)/$', 'edit_issue'),
                                  )


models_actions_patterns = patterns('help_desk.views',
                                   url(r'^$', 'model_list'),
                                   url(r'^add/$', 'model_add'),
                                   url(r'^edit/(?P<instance_id>\d+)/$', 'model_edit'),
                                   url(r'^remove/(?P<instance_id>\d+)/$', 'model_remove'),
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

