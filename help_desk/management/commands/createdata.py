#encoding: utf-8
from django.core.management.base import BaseCommand

from help_desk.models import BaseUser, ROLE_MANAGER, Client, Employee, Issue, \
    Service, ISSUE_TYPE_REQUEST, ISSUE_TYPE_INCIDENT


class Command(BaseCommand):
    help = 'Creates sample data.'

    def handle(self, *args, **options):
        print 'Cleaning'
        Client.objects.all().delete()
        Employee.objects.all().delete()
        BaseUser.objects.all().delete()#TODO: remove, make Client/Employee delete include BaseUser

        print 'Creating'
        print 'Sample employee account: admin admin'
        print 'Sample client account: client client'
        client = BaseUser.objects.create_client('client', 'client', 'UAB "Įmonė"', "Imonės g, Vilnius, Lietuva")
        employee = BaseUser.objects.create_employee('admin', 'admin', 'Petras', 'Petraitis', ROLE_MANAGER,
                                                    'petras@petraitis.lt', '865432100')
        employee_b = BaseUser.objects.create_employee('admin2', 'admin2', 'Antanas', 'Antanaitis', ROLE_MANAGER,
                                                     'antanas@antanaitis.lt', '865432101')

        service = Service.objects.create(description='Serverių hostingas', limit_inc=5, limit_req=2)
        issues = Issue.objects.create(type=ISSUE_TYPE_REQUEST, client=client, receive_type='phone',
                                         service=service)
        for i in range(10):
            r = Issue.objects.create(type=ISSUE_TYPE_INCIDENT, client=client, receive_type='phone', service=service)
            r.assign(employee_b, employee)

        issues.assign(employee_b, employee)
        issues.assign(employee, employee_b)
