from xlrd import open_workbook, sheet, cell
import models


def clean_database():
    models.Service.objects.all().delete()
    models.Client.objects.all().delete()
    models.Delegate.objects.all().delete()
    models.Request.objects.all().delete()
    models.Assignment.objects.all().delete()
    models.Contract.objects.all().delete()
    models.ContractService.objects.all().delete()
    models.Employee.objects.all().delete()

    models.BaseUser.objects.all().delete()


class XLSXImporter:
    
    def importXLSX(self, filename):
        book = open_workbook(filename)
        
        sheetPaslaugos = book.sheet_by_name("Paslaugos")
        sheetDarbuotojai = book.sheet_by_name("Darbuotojai")
        sheetKlientai = book.sheet_by_name("Klientai")
        sheetAtstovai = book.sheet_by_name("Atstovai")
        sheetSutartys = book.sheet_by_name("Sutartys")
        sheetSutPasl = book.sheet_by_name("SutPasl")
        sheetKreipiniai = book.sheet_by_name("Kreipiniai")
        sheetPaskyrimai = book.sheet_by_name("Paskyrimai")
        
    def parsePaslaugos(self, sheet):
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
        client = sheet.cell(i,2)
        first_name = sheet.cell(i,3)
        last_name = sheet.cell(i,4)
        phone_number = sheet.cell(i,5)
        email = sheet.cell(i,6)
        active = sheet.cell(i,7)
            
            
            