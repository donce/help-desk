import datetime

from xlrd import open_workbook, xldate_as_tuple
from django.db import transaction
from pytz import timezone
import pytz

from help_desk.models import Service, ROLE_ENGINEER, ROLE_MANAGER, ROLE_ADMINISTRATOR, Employee, Client, Issue, Contract, Assignment, BaseUser
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
import models

def clean_database():
    models.Service.objects.all().delete()
    models.Client.objects.all().delete()
    models.Delegate.objects.all().delete()
    models.Issue.objects.all().delete()
    models.Assignment.objects.all().delete()
    models.Contract.objects.all().delete()
    models.Employee.objects.all().delete()

    models.BaseUser.objects.all().delete()

class XLSXImporter:
    
    @transaction.commit_manually
    def import_xlsx(self, data, clear_all=True):
        try:
            print "Importing"
            book = open_workbook(file_contents=data.read())
            
            sheet_paslaugos = book.sheet_by_name("Paslaugos")
            sheet_darbuotojai = book.sheet_by_name("Darbuotojai")
            sheet_klientai = book.sheet_by_name("Klientai")
            sheet_atstovai = book.sheet_by_name("Atstovai")
            sheet_sutartys = book.sheet_by_name("Sutartys")
            sheet_sut_pasl = book.sheet_by_name("SutPasl")
            sheet_kreipiniai = book.sheet_by_name("Kreipiniai")
            sheet_paskyrimai = book.sheet_by_name("Paskyrimai")

            if clear_all:
                print 'clear db'
                clean_database()

            self.parse_paslaugos(sheet_paslaugos)
            self.parse_darbuotojai(sheet_darbuotojai)
            self.parse_klientai(sheet_klientai)
            self.parse_atstovai(sheet_atstovai)
            self.parse_sutartys(sheet_sutartys, book)
            self.parse_kreipiniai(sheet_kreipiniai, book)
            self.parse_paskyrimai(sheet_paskyrimai, book)
            self.parse_sut_pasl(sheet_sut_pasl)
            for s in Session.objects.all():
                s.delete()
        except Exception as e:
            print 'IMPORT ERROR'
            print '%s (%s)' % (e, type(e))
            transaction.rollback()
            return False
        else:
            transaction.commit()
            print 'Done!'
            return True

    def parse_paslaugos(self, sheet):
        print 'Parse paslaugos'
        for i in range(1, sheet.nrows):
            id = self.trim_id(sheet.cell(i, 0).value, "P")
            title = sheet.cell(i, 1).value
            limit_inc = sheet.cell(i, 2).value
            limit_req = sheet.cell(i, 3).value
            service = Service(id=id, title=title, limit_inc=limit_inc, limit_req=limit_req)
            service.save()

    def parse_darbuotojai(self, sheet):
        print 'Parse darbuotojai'
        for i in range(1, sheet.nrows):
            id = int(sheet.cell(i, 0).value)
            first_name = sheet.cell(i, 1).value
            last_name = sheet.cell(i, 2).value
            role = sheet.cell(i, 3).value
            phone_number = sheet.cell(i, 4).value
            email = sheet.cell(i, 5).value
            if role == 'I':
                role = ROLE_ENGINEER
            elif role == 'V':
                role = ROLE_MANAGER
            elif role == 'A':
                role = ROLE_ADMINISTRATOR

            username = email
            password = first_name
            userman = BaseUser.objects
            employee = userman.create_employee(username, password, first_name, last_name, role, email, phone_number)
            employee.save()

    def parse_klientai(self, sheet):
        print 'Parse klientai'
        for i in range(1, sheet.nrows):
            id = int(self.trim_id(sheet.cell(i, 0).value, "K"))
            title = sheet.cell(i, 1).value
            address = sheet.cell(i, 2).value

            client = Client(id=id, title=title, address=address)
            client.save()

    def parse_atstovai(self, sheet):
        print 'Parse atstovai'
        for i in range(1, sheet.nrows):
            id = int(sheet.cell(i, 0).value)
            client = Client.objects.get(id=int(self.trim_id(sheet.cell(i, 1).value, "K")))
            first_name = sheet.cell(i, 2).value
            last_name = sheet.cell(i, 3).value
            phone_number = sheet.cell(i, 4).value
            email = sheet.cell(i, 5).value
            #active = sheet.cell(i,7) #boolean?
            active = True

            username = email
            password = first_name
            userman = BaseUser.objects
            delegate = userman.create_delegate(client, email, password, first_name, last_name, phone_number)
            delegate.save()

    def parse_sutartys(self, sheet, workbook):
        print 'Parse sutartys'
        for i in range(1, sheet.nrows):
            id = int(sheet.cell(i, 0).value)
            number = sheet.cell(i, 1).value
            title = sheet.cell(i, 2).value
            client = Client.objects.get(id=int(self.trim_id(sheet.cell(i, 3).value, "K")))

            # FIXME : date tuple problem
            start = self.get_date(sheet.cell_value(i, 4), workbook)
            end = self.get_date(sheet.cell_value(i, 5), workbook)

            Contract.objects.create(id=id, number=number, title=title, client=client, start=start, end=end)

    def parse_kreipiniai(self, sheet, workbook):
        print 'Parse kreipiniai'
        for i in range(1, sheet.nrows):
            id = int(sheet.cell(i, 0).value)
            client = Client.objects.get(id=int(self.trim_id(sheet.cell(i, 1).value, "K")))
            service = Service.objects.get(id=int(self.trim_id(sheet.cell(i, 2).value, "P")))
            type = sheet.cell(i, 3).value
            receive_type = sheet.cell(i, 4).value
            title = 'imported'
            description = sheet.cell(i, 5).value

            created = self.get_date(sheet.cell(i, 6).value, workbook)
            closed = self.get_date(sheet.cell(i, 7).value, workbook)

            status = sheet.cell(i, 8).value
            if status == 'I':
                status = 'solved'
            elif status == 'P':
                status = 'in progress'
            elif status == 'A':
                status = 'rejected'
            elif status == 'N':
                status = 'unassigned'
            
            rating = sheet.cell(i, 9).value
            if rating == '':
                rating = 3
            else:
                rating = int(rating)

            # previous = None
            # if sheet.cell(i, 11).value:
            #     previous = Issue.objects.get(id=sheet.cell(i, 11).value)

            issue = Issue(id=id, client=client, service=service, type=type, status=status,
                          receive_type=receive_type, title=title, description=description,
                          created=created, closed=closed, rating=rating)
            issue.save()
    
    def parse_paskyrimai(self, sheet, workbook):
        print 'Parse paskyrimai'
        for i in range(1, sheet.nrows):
            id = int(sheet.cell(i, 0).value)
            issue = Issue.objects.get(id=int(sheet.cell(i, 1).value))
            assigned = Employee.objects.get(id=int(sheet.cell(i, 2).value))
            worker = Employee.objects.get(id=int(sheet.cell(i, 3).value))

            start = self.get_date(sheet.cell(i, 4).value, workbook)
            end = self.get_date(sheet.cell(i, 5).value, workbook)

            text = sheet.cell(i, 6).value
            time = int(sheet.cell(i, 8).value)

            assignment = Assignment(id=id, issue=issue, assigned=assigned,
                                    worker=worker, start=start, end=end, text=text, time=time)
            
            issue.current = assignment
            
            assignment.save()
            issue.save()

    def parse_sut_pasl(self, sheet):
        print 'Parse sutpasl'
        for i in range(1, sheet.nrows):
            contract = Contract.objects.get(id=int(sheet.cell(i, 0).value))
            service = Service.objects.get(id=int(self.trim_id(sheet.cell(i, 1).value, "P")))
            contract.services.add(service)
            contract.save()

    def get_date(self, value, workbook):
        if value:
            tuple = xldate_as_tuple(value, workbook.datemode)
            #tz = pytz.timezone(pytz.tzinfo)
            dt = datetime.date(*tuple[:3])
            #return tz.localize(dt)
            return dt;
        return None

    def get_datetime(self, value, workbook):
        if value:
            #tz = pytz.timezone(pytz.tzinfo)
            #print tz
            dt = datetime.datetime(*tuple)
            return dt;
            #return tz.localize(dt)
        return None

    def trim_id(self, id, prefix):
        return int(id.lstrip(prefix))
