#encoding: utf-8
from django.core.management.base import BaseCommand

from help_desk.models import BaseUser, ROLE_MANAGER, ROLE_ENGINEER, Client, \
        Employee, Issue, Service, ISSUE_TYPE_REQUEST, ISSUE_TYPE_INCIDENT, \
        Delegate


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

        client = BaseUser.objects.create_client('UAB "Įmonė"', "Imonės g, Vilnius, Lietuva")
        delegate = BaseUser.objects.create_delegate(client, 'client', 'client', 'Ponas', 'Klientas', '+37061234567')
        client2 = BaseUser.objects.create_client('UAB "ĮmonėsKonkurentai"', "ĮmonėsKonkurentų g. Vilnius, Lietuva")
        delegate2 = BaseUser.objects.create_delegate(client2, 'client2', 'client2', 'Ponas', 'KlientoKonkurentas', '+37061234568')


        employee = BaseUser.objects.create_employee('admin', 'admin', 'Petras', 'Petraitis', ROLE_MANAGER,
                                                    'petras@petraitis.lt', '865432100')
        employee_b = BaseUser.objects.create_employee('admin2', 'admin2', 'Antanas', 'Antanaitis', ROLE_MANAGER,
                                                     'antanas@antanaitis.lt', '865432101')
        engineer = BaseUser.objects.create_employee('engineer', 'engineer', 'Rytis', 'Karpuska', ROLE_ENGINEER,
                                                     'rytis@help-desk.lt', '12345')

        service = Service.objects.create(description='Serverių hostingas', limit_inc=5, limit_req=2)
        issue = client.register_issue(service, ISSUE_TYPE_REQUEST, 'phone', 'Problema', 'Neveikia kazkas...')
        for i in range(10):
            r = Issue.objects.create(title='test',  type=ISSUE_TYPE_INCIDENT, client=client, receive_type='phone', service=service)
            if i % 2 == 0:
                r.assign(employee_b, employee)

        issue.assign(employee_b, employee)
        issue.assign(employee, employee_b)
