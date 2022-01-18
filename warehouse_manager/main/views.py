from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseNotFound
from django.views import View
from django.views.generic import ListView, CreateView, FormView
from django.contrib.auth import logout

from .django_roser import RoseRocket
from .forms import TripCreation, ManifestSearch
from .models import *
from .utils import DataMixin

import requests
import datetime


def logout_user(request):
    logout(request)
    return render(request, 'main/logout.html')


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1> Page Not Found</h1>')


class WarehouseCommonPage(LoginRequiredMixin, DataMixin, ListView):
    model = Warehouses
    login_url = 'login'
    redirect_field_name = 'next'
    template_name = 'main/common_warehouse.html'
    context_object_name = 'warehouse'


class WarehouseView(LoginRequiredMixin, DataMixin, ListView):
    model = Tickets
    login_url = 'login'
    redirect_field_name = 'next'
    template_name = 'main/warehouse.html'
    context_object_name = 'ticks'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['file_dict'] = {}
        for tick in context['ticks']:
            associated_files = tick.ticketimage_set.all()
            files = {}
            for file in associated_files:
                if file.file.url[-3:] == 'pdf':
                    files[file] = 'pdf'
                else:
                    files[file] = 'jpg'
            context['file_dict'].update({tick: files})
            print(context['file_dict'])

        c_def = self.get_user_context(title='Ticket list',
                                      warehouse=Warehouses.objects.get(slug=self.kwargs['wh_slug']),
                                      wh_slug=self.kwargs['wh_slug'],
                                      # files=context['file_dict'],
                                      status_selected=self.request.GET.get('status', None),
                                      today=datetime.date.strftime(datetime.date.today(), '%Y-%m-%d')
                                      )
        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        status = self.request.GET.get('status', None)
        completion_date = self.request.GET.get('completed_at', None)
        if completion_date is None:
            completion_date = datetime.datetime.now()

        if status == 'Pending':
            return self.model.objects.filter(
                warehouse__slug=self.kwargs['wh_slug'], status='Pending')
        elif status == 'Completed':
            return self.model.objects.filter(
                warehouse__slug=self.kwargs['wh_slug'], status='Completed', completed__date=completion_date)
        else:
            return self.model.objects.filter(
                warehouse__slug=self.kwargs['wh_slug']).exclude(status='Completed')


class HomeView(LoginRequiredMixin, DataMixin, ListView):
    login_url = 'login'
    redirect_field_name = 'home'
    model = Warehouses
    template_name = 'main/home_page.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class TicketsView(LoginRequiredMixin, DataMixin, ListView):
    model = Tickets
    login_url = 'login'
    next_page = 'next'
    template_name = 'main/ticket_detail.html'
    context_object_name = 'ticket'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        associated_files = context['ticket'].ticketimage_set.all()
        files = {}
        for file in associated_files:
            if file.file.url[-3:] == 'pdf':
                files[file] = 'pdf'
            else:
                files[file] = 'jpg'
        print(files)
        c_def = self.get_user_context(title='Ticket details',
                                      ticket_files=files)
        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self, **kwargs):
        return Tickets.objects.get(warehouse__slug=self.kwargs['wh_slug'], pk=self.kwargs['tick_id'])



class CreateTicket(LoginRequiredMixin, DataMixin, FormView):
    model = Tickets
    login_url = 'login'
    next_page = 'next'
    template_name = 'main/ticket_creation.html'
    form_class = TripCreation
    success_url = 'warehouse'
    rose_rocket = RoseRocket()

    def post(self, request, *args, **kwargs):
        print(kwargs)
        print(args)
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('files')
        if form.is_valid():
            data = form.cleaned_data
            if form.cleaned_data['incoming'] == form.cleaned_data['outgoing']:
                print('one ticket')
                ticket = self.model(manifest_num=f'MENCM{form.cleaned_data["manifest"]}',
                                    order_nums=data['order_nums'],
                                    truck=data['truck'],
                                    trailer=data['trailer'],
                                    type='SPECIAL',
                                    consol=data['consol'],
                                    due_time=data['incoming_due_time'],
                                    created=datetime.datetime.now(),
                                    instructions=data['instructions'],
                                    user=self.request.user,
                                    warehouse=data['incoming'],
                                    status='Pending'
                                    )
                ticket.save()
                for f in files:
                    uploaded_file = TicketImage(ticket=ticket,
                                                file=f)
                    uploaded_file.save()

            else:
                ticket_one = self.model(manifest_num=f'MENCM{form.cleaned_data["manifest"]}',
                                        order_nums=data['order_nums'],
                                        truck=data['truck'],
                                        trailer=data['trailer'],
                                        type='INCOMING',
                                        consol=data['consol'],
                                        due_time=data['incoming_due_time'],
                                        created=datetime.datetime.now(),
                                        instructions=data['incoming_instructions'],
                                        user=self.request.user,
                                        warehouse=data['incoming'],
                                        status='Pending'
                                        )
                ticket_two = self.model(manifest_num=f'MENCM{form.cleaned_data["manifest"]}',
                                        order_nums=data['order_nums'],
                                        truck=data['truck'],
                                        trailer=data['trailer'],
                                        type='OUTGOING',
                                        consol=data['consol'],
                                        due_time=data['outgoing_due_time'],
                                        created=datetime.datetime.now(),
                                        instructions=data['outgoing_instructions'],
                                        user=self.request.user,
                                        warehouse=data['outgoing'],
                                        status='Pending'
                                        )
                ticket_one.save()
                ticket_two.save()
                for f in files:
                    uploaded_file = TicketImage(ticket=ticket_one,
                                                file=f)
                    uploaded_file1 = TicketImage(ticket=ticket_two,
                                                 file=f)
                    uploaded_file.save()
                    uploaded_file1.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        manifest = self.request.GET.get('manifest', None)
        if manifest is not None:
            manifest = f'MENCM{"".join([char for char in manifest if char.isdigit()])}'
            manifests = self.rose_rocket.get_manifest_by_number(manifest)
            print(manifests)
        else:
            manifests = []
        c_def = self.get_user_context(title='Ticket creation',
                                      manifest_list=[m['full_id'] for m in manifests]
                                      )

        return dict(list(context.items()) + list(c_def.items()))
    # def get(self, request, *args, **kwargs):
    #     manifest = self.request.GET.get('')
