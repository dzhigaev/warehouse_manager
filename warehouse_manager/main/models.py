from django.conf import settings
from django.db import models
from django.forms import ClearableFileInput
from django.urls import reverse

from core.settings import MEDIA_ROOT


class Tickets(models.Model):
    manifest_num = models.CharField(max_length=11, blank=True)
    order_nums = models.TextField(max_length=510, blank=False)
    truck = models.ForeignKey('Trucks', on_delete=models.PROTECT)
    trailer = models.ForeignKey('Trailers', on_delete=models.PROTECT)
    type = models.CharField(max_length=9)
    consol = models.BooleanField(blank=False, default=False)
    due_time = models.DateTimeField(blank=False)
    created = models.DateTimeField(auto_now=True)
    completed = models.DateTimeField(blank=True, null=True)
    # files = models.ForeignKey('TicketImage', on_delete=models.SET_NULL, null=True, blank=True)
    instructions = models.TextField(max_length=500, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    warehouse = models.ForeignKey('Warehouses', on_delete=models.PROTECT)
    status = models.CharField(max_length=10, default='Pending')

    def __str__(self):
        return f'{self.pk}//{self.manifest_num}//{self.due_time}//{self.status}'

    def get_absolute_url(self):
        return reverse('ticket', kwargs={'tick_id': self.pk,
                                         'wh_slug': self.warehouse.slug,
                                         })

    class Meta:
        ordering = ['due_time', 'pk']


class TicketImage(models.Model):
    ticket = models.ManyToManyField('Tickets', blank=False)
    file = models.FileField(blank=True, upload_to='ticket_files/%Y/%m/%d', max_length=255)
    external_url = models.URLField(blank=True)

    # class Meta:
    #     ordering = ['ticket']

    def __str__(self):
        return f'{self.pk}//{self.file}'

    def get_absolute_url(self):
        return reverse('file', kwargs={'file_id': self.pk,
                                       'file_name': self.file,
                                       })


class WarehouseReply(models.Model):
    ticket = models.ForeignKey('Tickets', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    warehouse = models.ForeignKey('Warehouses', on_delete=models.DO_NOTHING)
    comments = models.TextField(max_length=400, blank=True)
    # files = models.FileField(blank=True, upload_to=MEDIA_ROOT.strip('/'))

    def __str__(self):
        return str(self.ticket.pk)

    class Meta:
        ordering = ['ticket']

    def get_absolute_url(self):
        return reverse('reply', kwargs={'tick_id': self.ticket.pk,
                                        'wh_slug': self.warehouse.slug,
                                        })


class ReplyImage(models.Model):
    reply = models.ManyToManyField('WarehouseReply', blank=False)
    file = models.FileField(blank=True, upload_to='replyfiles/%Y/%m/%d', max_length=255)

    def __str__(self):
        return f'{self.pk}//{self.file}'


class Warehouses(models.Model):
    name = models.CharField(max_length=30, db_index=True, unique=True)
    location = models.CharField(max_length=100)
    slug = models.SlugField(max_length=25, unique=True, blank=False, db_index=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('warehouse', kwargs={'wh_slug': self.slug})

    # personel = models.

    class Meta:
        ordering = ['name', 'location']


class Trucks(models.Model):
    name = models.CharField(max_length=10, db_index=True, unique=True)
    available = models.CharField(max_length=20)
    comments = models.TextField(max_length=300, blank=True)
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Trailers(models.Model):
    name = models.CharField(max_length=10, db_index=True, unique=True)
    status = models.CharField(max_length=20, blank=True)
    available = models.CharField(max_length=20)
    comments = models.TextField(max_length=300, blank=True)

    def __str__(self):
        return self.name
