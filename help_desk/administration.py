from xlrd import open_workbook
from help_desk.models import Service, ROLE_ENGINEER, ROLE_MANAGER, ROLE_ADMINISTRATOR, Employee, Client, Issue, Contract, Delegate, UserManager
import models
import xlrd
import datetime


def clean_database():
    models.Service.objects.all().delete()
    models.Client.objects.all().delete()
    models.Delegate.objects.all().delete()
    models.Issue.objects.all().delete()
    models.Assignment.objects.all().delete()
    models.Contract.objects.all().delete()
    models.ContractService.objects.all().delete()
    models.Employee.objects.all().delete()

    models.BaseUser.objects.all().delete()


class XLSXImporter:
    def import_xlsx(self, data):
        book = open_workbook(file_contents=data.read())

        sheet_paslaugos = book.sheet_by_name("Paslaugos")
        sheet_darbuotojai = book.sheet_by_name("Darbuotojai")
        sheet_klientai = book.sheet_by_name("Klientai")
        sheet_atstovai = book.sheet_by_name("Atstovai")
        sheet_sutartys = book.sheet_by_name("Sutartys")
        sheet_sut_pasl = book.sheet_by_name("SutPasl")
        sheet_kreipiniai = book.sheet_by_name("Kreipiniai")
        sheet_paskyrimai = book.sheet_by_name("Paskyrimai")

        self.parsePaslaugos(sheet_paslaugos)
        self.parseDarbuotojai(sheet_darbuotojai) # TODO : user
        self.parseKlientai(sheet_klientai)
        self.parseAtstovai(sheet_atstovai) # TODO : user
        self.parseSutartys(sheet_sutartys, book) # FIXME : tuple to date
        #self.parseKreipiniai(sheet_kreipiniai, book) # FIXME : date tuple problem
        #self.parsePaskyrimai(sheet, book) # FIXME : tuple to date
        #self.parseSutPasl(sheet_sut_pasl)
        
    def parsePaslaugos(self, sheet):
        for i in range(1, sheet.nrows):
            id = self.trimID(sheet.cell(i, 0).value, "P")
            description = sheet.cell(i, 1).value
            limit_inc = sheet.cell(i, 2).value
            limit_req = sheet.cell(i, 3).value
            service = Service(id=id, description=description, limit_inc=limit_inc, limit_req=limit_req)
            service.save()

    def parseDarbuotojai(self, sheet):
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

            userManager = UserManager()
            username = email
            password = first_name
            employee = userManager.create_employee(username, password, first_name, last_name, role, email, phone_number)
            employee.save()

    def parseKlientai(self, sheet):
        for i in range(1, sheet.nrows):
            id = int(self.trimID(sheet.cell(i, 0).value, "K"))
            title = sheet.cell(i, 1).value
            address = sheet.cell(i, 2).value

            client = Client(id=id, title=title, address=address)
            client.save()

    def parseAtstovai(self, sheet):
        for i in range(1, sheet.nrows):
            id = int(sheet.cell(i, 0).value)
            client = Client.objects.get(id=int(self.trimID(sheet.cell(i, 1).value, "K")))
            first_name = sheet.cell(i, 2).value
            last_name = sheet.cell(i, 3).value
            phone_number = sheet.cell(i, 4).value
            email = sheet.cell(i, 5).value
            #active = sheet.cell(i,7) #boolean?
            active = True
            
            userManager = UserManager()
            username = email
            password = first_name
            delegate = userManager.create_delegate(client, email, password, first_name, last_name, phone_number)
            delegate.save()

    def parseSutartys(self, sheet, workbook):
        for i in range(1, sheet.nrows):
            id = int(sheet.cell(i, 0).value)
            number = sheet.cell(i, 1).value
            title = sheet.cell(i, 2).value
            client = Client.objects.get(id=int(self.trimID(sheet.cell(i, 3).value, "K")))
            
            # FIXME : date tuple problem
            start = self.get_date(sheet.cell_value(i, 4), workbook)
            end = self.get_date(sheet.cell_value(i, 5), workbook)

            Contract.objects.create(id=id, number=number, title=title, client=client, start=start, end=end)

    def parseKreipiniai(self, sheet, workbook):
        for i in range(1, sheet.nrows):
            id = int(sheet.cell(i, 0).value)
            client = Client.objects.get(id=int(self.trimID(sheet.cell(i, 1).value, "K")))
            service = Service.objects.get(id=int(self.trimID(sheet.cell(i, 2).value, "P")))
            type = sheet.cell(i, 3).value
            receive_type = sheet.cell(i, 4).value
            #title = sheet.cell(i, 5).value
            description = sheet.cell(i, 5).value
            
            # FIXME : date tuple problem
            createdTuple = xlrd.xldate_as_tuple(sheet.cell(i, 6).value, workbook.datemode)
            created = datetime.datetime(*createdTuple)
            closedTuple = xlrd.xldate_as_tuple(sheet.cell(i, 7).value, workbook.datemode)
            closed = datetime.datetime(*closedTuple)
            
            #status = sheet.cell(i, 8).value
            rating = int(sheet.cell(i, 9).value)
            #current = sheet.cell(i, 10).value # TODO : what?
            #previous = sheet.cell(i, 11).value # TODO : purpose of this?
            issue = Issue(id=id, client=client, service=service, type=type,
                          receive_type=receive_type, description=description, 
                          created=created, closed=closed, rating=rating)
            issue.save()

    def parsePaskyrimai(self, sheet, workbook):
        for i in range(1, sheet.nrows):
            id = int(sheet.cell(i, 0).value)
            issue = Issue.objects.get(id=int(sheet.cell(i, 1).value))
            assigned = Employee.objects.get(id=int(sheet.cell(i, 2).value))
            worker = Employee.objects.get(id=int(sheet.cell(i, 3).value))
            
            # FIXME : date tuple problem
            startTuple = xlrd.xldate_as_tuple(sheet.cell(i, 4).value, workbook.datemode)
            start = datetime.datetime(*startTuple)
            endTuple = xlrd.xldate_as_tuple(sheet.cell(i, 5).value, workbook.datemode)
            end = datetime.datetime(*endTuple)
            
            text = sheet.cell(i, 6).value
            time = int(sheet.cell(i, 8).value)
            
            assignment = Assignment(id=id, issue=issue, assigned=assigned,
                        worker=worker, start=start, end=end, text=text, time=time)

    def parseSutPasl(self, sheet):
        for i in range(1, sheet.nrows):
            contract = Contract.objects.get(id=int(sheet.cell(i, 0).value))
            service = Service.objects.get(id=int(self.trimID(sheet.cell(i, 1).value, "P")))
            contract.services.add(service)

    def get_date(self, value, workbook):
        if value:
            tuple = xlrd.xldate_as_tuple(value, workbook.datemode)
            return datetime.date(*tuple[:3])
        return None

    def get_datetime(self, value, workbook):
        if value:
            tuple = xlrd.xldate_as_tuple(value, workbook.datemode)
            return datetime.datetime(*tuple)
        return None

    def trimID(self, id, prefix):
        return int(id.lstrip(prefix))
