from django.contrib import admin
import models

admin.site.register(models.Service)
admin.site.register(models.Client)
admin.site.register(models.ClientPhoneNumber)
admin.site.register(models.ClientEmail)
admin.site.register(models.Request)
admin.site.register(models.Contract)
admin.site.register(models.ContractService)
admin.site.register(models.Employee)
