# encoding=utf-8
from datetime import datetime

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

    def create_client(self, title, address):
        client = Client.objects.create(title=title, address=address)
        return client

    def create_delegate(self, client, email, password, first_name, last_name, phone_number):
        user = self.create_user(email, password)
        delegate = Delegate.objects.create(user=user, client=client, first_name=first_name, last_name=last_name,
                                           phone_number=phone_number)
        return delegate

    def create_employee(self, username, password, first_name, last_name, role, email, phone_number):
        user = self.create_user(username, password)
        employee = Employee.objects.create(user=user, first_name=first_name, last_name=last_name,
                                           role=role, email=email, phone_number=phone_number)
        return employee


class BaseUser(AbstractBaseUser):
    username = models.CharField(_('Username'), max_length=40, unique=True, db_index=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def is_active(self):
        return True

    def get_full_name(self):
        if self.is_delegate():
            return self.delegate.__unicode__()
        elif self.is_employee():
            return self.employee.__unicode__()
        return self.get_short_name()

    def __unicode__(self):
        return self.get_full_name()

    def get_short_name(self):
        return self.username

    def is_staff(self):
        return self.is_superuser #TODO: check keys

    def has_module_perms(self, perm):
        return True

    def has_perm(self, perm):
        return True

    def is_delegate(self):
        try:
            self.delegate
            return True
        except Delegate.DoesNotExist:
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
    title = models.CharField(_('Title'), max_length=255)
    limit_inc = models.IntegerField(_('Incident limit'))
    limit_req = models.IntegerField(_('Request limit'))

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('help_desk.views.model_edit', args=('service', self.id))


class Client(models.Model):
    title = models.CharField(_('Title'), max_length=255)
    address = models.CharField(_('Address'), max_length=255)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('help_desk.views.model_edit', args=('client', self.id))

    def register_issue(self, service, type, receive_type, title, description):
        return Issue.objects.create(client=self, service=service, type=type, receive_type=receive_type,
                                    title=title, description=description)

    def get_current_contracts(self):
        #TODO: return only current contracts
        return Contract.objects.filter(client=self)

    def get_current_services(self):
        services = []
        for contract in self.get_current_contracts():
            for service in contract.services.all():
                services.append(service)
        return services

class Delegate(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    client = models.ForeignKey(Client, verbose_name=_('Client'))
    first_name = models.CharField(_('First name'), max_length=255)
    last_name = models.CharField(_('Last name'), max_length=255)
    phone_number = models.CharField(_('Phone number'), max_length=PHONE_NUMBER_MAX_LENGTH)
    email = models.CharField(_('Email'), max_length=255)
    active = models.BooleanField(_('Active'), default=True)

    def __unicode__(self):
        return '{0} {1} ({2})'.format(self.first_name, self.last_name, self.client)


ISSUE_TYPE_INCIDENT = 'INC'
ISSUE_TYPE_REQUEST = 'REQ'

ISSUE_TYPE_CHOICES = (
    (ISSUE_TYPE_INCIDENT, _('Incident')),
    (ISSUE_TYPE_REQUEST, _('Request')),
)

ISSUE_RECEIVE_TYPE_WEBSITE = 'website'

ISSUE_RECEIVE_TYPE_CHOICES = (
    ('phone', _('By phone')),
    ('email', _('By e-mail')),
    (ISSUE_RECEIVE_TYPE_WEBSITE, _('By website')),
)

#TODO: add statuses
ISSUE_STATUS_UNASSIGNED = 'unassigned'

ISSUE_STATUS_CHOICES = (
    (ISSUE_STATUS_UNASSIGNED, _('Unassigned')),
    ('in progress', _('In Progress')),
    ('solved', _('Solved')),
    ('rejected', _('Rejected')),
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
    status = models.CharField(_('Status'), choices=ISSUE_STATUS_CHOICES, max_length=255, default=ISSUE_STATUS_UNASSIGNED)
    rating = models.PositiveIntegerField(_('Rating'), null=True)
    current = models.ForeignKey('Assignment', related_name='current', null=True, blank=True)
    previous = models.ForeignKey('Issue', null=True, blank=True)#TODO: purpose of this?

    def solve(self):
        self.status = 'solved'
        self.closed = datetime.now()
        self.save()

    def reject(self):
        self.status = 'rejected'
        self.closed = datetime.now()
        self.save()

    def returnIssue(self):
        self.status = 'unassigned'
        self.current = None
        self.assigned_to = None
        self.save()

    def assign(self, assigned, worker):
        assignment = Assignment.objects.create(issue=self, assigned=assigned, worker=worker)
        #if (self.current)
        #self.current.end = NOW
        self.current = assignment
        self.status = 'in progress'
        self.save()

    def get_absolute_url(self, edit=None):
        if edit == None:
            edit = False
        if (edit):
            return reverse('help_desk.views.edit_issue', args=(self.id,))
        else:
            return reverse('help_desk.views.view_issue', args=(self.id,))

    def __unicode__(self):
        return self.title


class Assignment(models.Model):
    issue = models.ForeignKey('Issue', verbose_name=_('Issue'))
    assigned = models.ForeignKey('Employee', related_name='assigned')
    worker = models.ForeignKey('Employee', related_name='working')
    start = models.DateTimeField(_('Start'), auto_now_add=True)
    end = models.DateTimeField(_('End'), null=True)
    text = models.TextField(_('Text'))
    #TODO: result
    time = models.PositiveIntegerField(null=True)

    def __unicode__(self):
        return self.worker.first_name + ' ' + self.worker.last_name


class Contract(models.Model):
    number = models.CharField(_('Number'), max_length=255)
    title = models.CharField(_('Title'), max_length=255)
    client = models.ForeignKey(Client, verbose_name=_('Client'))
    start = models.DateField(_('Start'))
    end = models.DateField(_('End'), null=True, blank=True)
    services = models.ManyToManyField('Service', related_name='contracts')

    def get_absolute_url(self):
        return reverse('help_desk.views.model_edit', args=('contract', self.id))


ROLE_ENGINEER = 'engineer'
ROLE_ADMINISTRATOR = 'administrator'
ROLE_MANAGER = 'manager'

ROLE_CHOICES = (
    (ROLE_ENGINEER, _('Engineer')),
    (ROLE_ADMINISTRATOR, _('Administrator')),
    (ROLE_MANAGER, _('Manager')),
)


class Employee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    first_name = models.CharField(_('First name'), max_length=255)
    last_name = models.CharField(_('Last name'), max_length=255)
    role = models.CharField(_('Role'), choices=ROLE_CHOICES, max_length=255)
    phone_number = models.CharField(_('Phone number'), max_length=PHONE_NUMBER_MAX_LENGTH)
    email = models.CharField(_('Email'), max_length=255)

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

    def can_view_statistics(self):
        return self.is_manager()

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


class Deflection(models.Model):
    value = models.IntegerField(_('Time deflection'))



