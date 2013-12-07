from xlrd import open_workbook, sheet, cell
from help_desk import models
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


    def parse_paslaugos(self, sheet):
        for i in range(sheet.nrows):
            service.description = sheet.cell(i, B)
            print service.description # TODO: remove
            # TODO: fix models / think how to map everything to models