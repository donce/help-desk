from xlrd import open_workbook, sheet, cell
import models


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
    def import_xlsx(self, filename):
        book = open_workbook(filename)

        sheet_paslaugos = book.sheet_by_name("Paslaugos")
        sheet_darbuotojai = book.sheet_by_name("Darbuotojai")
        sheet_klientai = book.sheet_by_name("Klientai")
        sheet_atstovai = book.sheet_by_name("Atstovai")
        sheet_sutartys = book.sheet_by_name("Sutartys")
        sheet_sut_pasl = book.sheet_by_name("SutPasl")
        sheet_kreipiniai = book.sheet_by_name("Kreipiniai")
        sheet_paskyrimai = book.sheet_by_name("Paskyrimai")
        
        parse_paslaugos(sheet_paslaugos)
        parse_darbuotojai(sheet_darbuotojai)


    def parse_paslaugos(self, sheet):
        for i in range(sheet.nrows):
            description = sheet.cell(i, 2)
            limit_inc = sheet.cell(i, 3)
            limit_req = sheet.cell(i, 4)
            service = Service(description=description, limit_inc=limit_inc, limit_req=limit_req)
            service.save()
            
    def parseDarbuotojai(self, sheet):
        for i in range(sheet.nrows):
            first_name = sheet.cell(i,2)
            last_name = sheet.cell(i,3)
            role = sheet.cell(i,4)
            phone_number = sheet.cell(i,5)
            email = sheet.cell(i,6)
            
            if role == 'I':
                role = ROLE_ENGINEER
            elif role == 'V':
                role = ROLE_MANAGER
            elif role == 'A':
                role = ROLE_ADMINISTRATOR
            
            # TODO : user ???
            employee = Employee(first_name=first_name, last_name=last_name, role=role, phone_number=phone_number, email=email)
            employee.save()
            
    def parseKlientai(self, sheet):
        for i in range(sheet.nrows):
            title = sheet.cell(i,2)
            address = sheet.cell(i,3)
            
            # TODO : user ???
            client = Client(title=title, address=address)
            client.save()
            
    def parseAtstovai(self, sheet):
        for i in range(sheet.nrows):
            client = sheet.cell(i,2)
            first_name = sheet.cell(i,3)
            last_name = sheet.cell(i,4)
            phone_number = sheet.cell(i,5)
            email = sheet.cell(i,6)
            active = sheet.cell(i,7) #boolean?
            delegate = Delegate(client = client, first_name=first_name, last_name=last_name, phone_number=phone_number, email=email, active=active)
            delegate.save()
            
    def parseSutartys(self, sheet):
        for i in range(sheet.nrows):
            id = sheet.cell(i,1)
            number = sheet.cell(i,2)
            title = sheet.cell(i,3)
            client = sheet.cell(i,4)
            start = sheet.cell(i,5)
            end = sheet.cell(i,6)
            contract = Contract(id=id, number=number, title=title, client=client, start=start, end=end)
            contract.save()
        
    def parseKreipiniai(self, sheet):
        for i in range(sheet.nrows):
            id = sheet.cell(i,1)
            client = sheet.cell(i,2)
            service = sheet.cell(i,3)
            type = sheet.cell(i,4)
            receive_type = sheet.cell(i,5)
            title = sheet.cell(i,6)
            description = sheet.cell(i,7)
            created = sheet.cell(i,8)
            closed = sheet.cell(i,9)
            status = sheet.cell(i,10)
            rating = sheet.cell(i,11)
            current = sheet.cell(i,12)
            previous = sheet.cell(i,13) #TODO: purpose of this?
            issue = Issue(id=id, client=client, service=service, type=type, receive_type=receive type, title=title, description=description, created=created, closed=closed, status=status, rating=rating, current=current, previous=previous)
            issue.save()
            
            
        
        
        
         
            
