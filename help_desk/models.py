from django.db import models

class Service(models.Model):
	description = models.TextField()

class Client(models.Model):
	title = models.CharField(max_length=255)
	address = models.CharField(max_length=255)

class Contract(models.Model):
	client = models.ForeignKey(Client)

class ContractService(models.Model):
	contract = models.ForeignKey(Contract)
	service = models.ForeignKey(Service)

#TODO: primary key
