from xlrd import open_workbook, sheet, cell
import models

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
            service.description = sheet.cell(i, B)
            print service.description # TODO: remove
            # TODO: fix models / think how to map everything to models