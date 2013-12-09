# encoding=utf-8
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.urlresolvers import reverse
from django.db import models

from django.utils.translation import ugettext_lazy as _

PHONE_NUMBER_MAX_LENGTH = 20


class UserManager(BaseUserManager):
    def create_user(self, username, password=None):
        user = self.model(username=username)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password):
        user = self.create_user(username, password)
        user.is_superuser = True
        user.save()
        return user

    def create_client(self, username, password, title, address):
        user = self.create_user(username, password)
        client = Client.objects.create(user=user, title=title, address=address)
        return client

    def create_employee(self, username, password, first_name, last_name, role, email, phone_number):
        user = self.create_user(username, password)
        employee = Employee.objects.create(user=user, first_name=first_name, last_name=last_name,
                                           role=role, email=email, phone_number=phone_number)
        return employee


class BaseUser(AbstractBaseUser):
    username = models.CharField(max_length=40, unique=True, db_index=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def is_active(self):
        return True

    def get_full_name(self):
        #TODO: return company name/first name-second name, depending on type
        return self.get_short_name()

    def get_short_name(self):
        return self.username

    def is_staff(self):
        return self.is_superuser #TODO: check keys

    def has_module_perms(self, perm):
        return True

    def has_perm(self, perm):
        return True

    def is_client(self):
        try:
            self.client
            return True
        except Client.DoesNotExist:
            return False

    def is_employee(self):
        try:
            self.employee
            return True
        except Employee.DoesNotExist:
            return False

    #TODO: needed? if yes, then get_client
    def get_employee(self):
        try:
            return self.employee
        except Employee.DoesNotExist:
            return None


class Service(models.Model):
    #TODO: id - string?
    description = models.TextField(_('Description'))
    limit_inc = models.IntegerField(_('Incident limit'))
    limit_req = models.IntegerField(_('Request limit'))

    def __unicode__(self):
        return self.description
    def get_absolute_url(self):
        return reverse('help_desk.views.model_edit', args=('client', self.id))


class Client(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    title = models.CharField(_('Title'), max_length=255)
    address = models.CharField(_('Address'), max_length=255)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('help_desk.views.model_edit', args=('client', self.id))


class Delegate(models.Model):
    client = models.ForeignKey(Client, verbose_name=_('Client'))
    first_name = models.CharField(_('First name'), max_length=255)
    last_name = models.CharField(_('Last name'), max_length=255)
    phone_number = models.CharField(_('Phone number'), max_length=PHONE_NUMBER_MAX_LENGTH)
    email = models.CharField(_('Email'), max_length=255)
    active = models.BooleanField(_('Active'), default=True)


ISSUE_TYPE_INCIDENT = 'INC'
ISSUE_TYPE_REQUEST = 'REQ'

ISSUE_TYPE_CHOICES = (
    (ISSUE_TYPE_INCIDENT, 'Incident'),
    (ISSUE_TYPE_REQUEST, 'Request'),
)

ISSUE_RECEIVE_TYPE_CHOICES = (
    ('phone', 'Telefonu'),
    ('email', 'El. paštu'),
    ('website', 'Savitarnos svetainėje'),
)

#TODO: add statuses
ISSUE_STATUS_CHOICES = (
    ('solved', 'Solved'),
    ('rejected', 'Rejected'),
)


class Issue(models.Model):
    client = models.ForeignKey(Client, verbose_name=_('Client'))
    service = models.ForeignKey(Service, verbose_name=_('Service'))
    type = models.CharField(_('Type'), choices=ISSUE_TYPE_CHOICES, max_length=255)
    receive_type = models.CharField(_('Receive type'), choices=ISSUE_RECEIVE_TYPE_CHOICES, max_length=255)
    title = models.CharField(_('Title'), max_length=255)
    description = models.TextField(_('Description'))
    created = models.DateTimeField(_('Created'), auto_now_add=True)
    closed = models.DateTimeField(_('Closed'), null=True)
    status = models.CharField(_('Status'), choices=ISSUE_STATUS_CHOICES, max_length=255)
    rating = models.PositiveIntegerField(_('Rating'), null=True)
    current = models.ForeignKey('Assignment', related_name='current', null=True)
    previous = models.ForeignKey('Issue', null=True)#TODO: purpose of this?

    def assign(self, assigned, worker):
        assignment = Assignment.objects.create(issue=self, assigned=assigned, worker=worker)
        #if (self.current)
        #self.current.end = NOW
        self.current = assignment
        self.save()


class Assignment(models.Model):
    issue = models.ForeignKey('Issue')
    assigned = models.ForeignKey('Employee', related_name='assigned')
    worker = models.ForeignKey('Employee', related_name='working')
    start = models.DateTimeField(auto_now_add=True)
    end = models.DateTimeField(null=True)
    text = models.TextField()
    #TODO: result
    time = models.PositiveIntegerField(null=True)


class Contract(models.Model):
    number = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    client = models.ForeignKey(Client)
    start = models.DateField()
    end = models.DateField()

    def get_absolute_url(self):
        return reverse('help_desk.views.model_edit', args=('contract', self.id))


class ContractService(models.Model):
    contract = models.ForeignKey(Contract)
    service = models.ForeignKey(Service)

    class Meta:
        unique_together = ('contract', 'service')


ROLE_ENGINEER = 'engineer'
ROLE_ADMINISTRATOR = 'administrator'
ROLE_MANAGER = 'manager'

ROLE_CHOICES = (
    (ROLE_ENGINEER, 'Inžinierius'),
    (ROLE_ADMINISTRATOR, 'Administratorius'),
    (ROLE_MANAGER, 'Vadovas'),
)


class Employee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    role = models.CharField(choices=ROLE_CHOICES, max_length=255)
    phone_number = models.CharField(max_length=PHONE_NUMBER_MAX_LENGTH)
    email = models.CharField(max_length=255)

    def is_engineer(self):
        return self.role == ROLE_ENGINEER

    def is_administrator(self):
        return self.role == ROLE_ADMINISTRATOR

    def is_manager(self):
        return self.role == ROLE_MANAGER

    def can_solve_issues(self):
        return self.is_engineer() or self.is_manager()

    def can_manage_issues(self):
        return self.is_administrator() or self.is_manager()

    def can_reassign_issues(self):
        return self.is_manager()

    def can_manage_models(self):
        # return False
        return self.is_administrator() or self.is_manager()

    def can_administrate(self):
        return self.is_administrator() or self.is_manager()

    def has_permission(self, permission):
        print 'can_' + permission

    def title(self):
        return u'{0} {1} ({2})'.format(self.first_name, self.last_name, self.get_role_display())

    def __unicode__(self):
        return self.title()

    def get_absolute_url(self):
        return reverse('help_desk.views.model_edit', args=('employee', self.id))

    def issues(self):
        return Issue.objects.filter(current__worker=self)
