# encoding=utf8
from django.db import models

PHONE_NUMBER_MAX_LENGTH = 20

class Service(models.Model):
	description = models.TextField()

class Client(models.Model):
	title = models.CharField(max_length=255)
	address = models.CharField(max_length=255)

class ClientPhoneNumber(models.Model):
	client = models.ForeignKey(Client)
	phone_number = models.CharField(max_length=PHONE_NUMBER_MAX_LENGTH)
	
class ClientEmail(models.Model):
	client = models.ForeignKey(Client)
	email = models.CharField(max_length=255)


#TODO: rename request model
REQUEST_TYPE_INCIDENT = 'INC'
REQUEST_TYPE_REQUEST = 'REQ'

REQUEST_TYPE_CHOICES = (
	(REQUEST_TYPE_INCIDENT, 'Incident'),
	(REQUEST_TYPE_REQUEST, 'Request'),
)

class Request(models.Model):
	type = models.CharField(choices=REQUEST_TYPE_CHOICES, max_length=255)
	client = models.ForeignKey(Client)
	#gavimo būdas
	service = models.ForeignKey(Service)
	created = models.DateTimeField(auto_now_add=True)
	closed = models.DateTimeField()

class Contract(models.Model):
	client = models.ForeignKey(Client)
	start = models.DateField()
	end = models.DateField()

class ContractService(models.Model):
	contract = models.ForeignKey(Contract)
	service = models.ForeignKey(Service)
#TODO: primary key

ROLE_ENGINEER = 'engineer'
ROLE_ADMINISTRATOR = 'administrator'
ROLE_MANAGER = 'manager'

ROLE_CHOICES = (
	(ROLE_ENGINEER, 'Engineer'),
	(ROLE_ADMINISTRATOR, 'Administrator'),
	(ROLE_MANAGER, 'Manager'),
)

class Employee(models.Model):
	first_name = models.CharField(max_length=255)
	last_name = models.CharField(max_length=255)
	role = models.CharField(choices=ROLE_CHOICES, max_length=255)
	email = models.CharField(max_length=255)
	phone_number = models.CharField(max_length=PHONE_NUMBER_MAX_LENGTH)
