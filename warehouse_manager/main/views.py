import json

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseNotFound
from django.views import View
from django.db.models import Q
from django.views.generic import ListView, CreateView, FormView, TemplateView
from django.contrib.auth import logout

from .django_roser import RoseRocket
from .forms import TripCreation, WarehouseReplyForm, DeleteForm
from .models import Warehouses, Tickets, WarehouseReply, ReplyImage, TicketImage
from .utils import DataMixin

import requests
import datetime


def logout_user(request):
    logout(request)
    return render(request, 'main/logout.html')


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1> Page Not Found</h1>')


class WarehouseCommonPage(LoginRequiredMixin, DataMixin, ListView):
    """Page with list of warehouses"""
    model = Warehouses
    login_url = 'login'
    redirect_field_name = 'next'
    template_name = 'main/common_warehouse.html'
    context_object_name = 'warehouse'


class WarehouseView(LoginRequiredMixin, DataMixin, ListView):
    """Page for one warehouse with list of tickets with short description"""
    model = Tickets
    login_url = 'login'
    redirect_field_name = 'next'
    template_name = 'main/warehouse.html'
    context_object_name = 'ticks'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['file_dict'] = {}
        r = self.request.GET.get('search', None)
        if r is not None:
            my_search = f'Search results for: {r}'
        else:
            my_search = ''
        for tick in context['ticks']:
            associated_files = tick.ticketimage_set.all()
            files = {}
            for file in associated_files:
                if bool(file.file):
                    if file.file.url[-3:] == 'pdf':
                        files[file] = 'pdf'
                    else:
                        files[file] = 'jpg'
            context['file_dict'].update({tick: files})

        c_def = self.get_user_context(title='Ticket list',
                                      warehouse=Warehouses.objects.get(slug=self.kwargs['wh_slug']),
                                      wh_slug=self.kwargs['wh_slug'],
                                      # files=context['file_dict'],
                                      status_selected=self.request.GET.get('status', None),
                                      today=datetime.date.strftime(datetime.date.today(), '%Y-%m-%d'),
                                      searching=my_search,
                                      )
        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        status = self.request.GET.get('status', None)
        completion_date = self.request.GET.get('completed_at', None)
        search = self.request.GET.get('search', None)
        if search is not None:
            try:
                lookups = Q(pk=search)
                result = self.model.objects.filter(
                    lookups,
                    warehouse__slug=self.kwargs['wh_slug'],
                ).distinct()
            except:
                lookups = Q(manifest_num=search) | Q(order_nums__icontains=search)
                result = self.model.objects.filter(
                    lookups,
                    warehouse__slug=self.kwargs['wh_slug']
                ).distinct()
            return result
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
                warehouse__slug=self.kwargs['wh_slug']).exclude(status='Completed').exclude(status='Deleted')


class HomeView(LoginRequiredMixin, DataMixin, ListView):
    login_url = 'login'
    redirect_field_name = 'home'
    model = Warehouses
    template_name = 'main/home_page.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class TicketsView(LoginRequiredMixin, DataMixin, ListView):
    """Details of one ticket"""
    model = Tickets
    login_url = 'login'
    next_page = 'next'
    template_name = 'main/ticket_detail.html'
    context_object_name = 'ticket'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        associated_files = context['ticket'].ticketimage_set.all()
        files = {}
        for file in [file for file in associated_files if file is not None]:
            if bool(file.file):
                if file.file.url[-3:] == 'pdf':
                    files[file] = 'pdf'
                else:
                    files[file] = 'jpg'
        c_def = self.get_user_context(title='Ticket details',
                                      ticket_files=files,
                                      ticket_urls=enumerate(
                                          [url.external_url for url in associated_files if bool(url.external_url)],
                                          start=1,
                                      ),
                                      wh_slug=self.kwargs['wh_slug'],
                                      form=WarehouseReplyForm(),
                                      tick_id=self.kwargs['tick_id'],
                                      reply=WarehouseReply.objects.filter(ticket=self.kwargs['tick_id']).first(),
                                      reply_doc=ReplyImage.objects.filter(
                                          reply=WarehouseReply.objects.filter(ticket=self.kwargs['tick_id']).first())
                                      )
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
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('files')

        if form.is_valid():
            url = form.cleaned_data['files_url'].split('  ')
            data = form.cleaned_data
            if form.cleaned_data['incoming'] == form.cleaned_data['outgoing']:
                ticket = self.model(manifest_num=f'{form.cleaned_data["manifest"]}',
                                    order_nums=data['order_nums'],
                                    truck=data['truck'],
                                    trailer=data['trailer'],
                                    type='SPECIAL',
                                    consol=data['consol'],
                                    due_time=data['incoming_due_time'],
                                    created=datetime.datetime.now(),
                                    instructions=data['incoming_instructions'] + data['outgoing_instructions'],
                                    user=self.request.user,
                                    warehouse=data['incoming'],
                                    status='Pending'
                                    )
                ticket.save()
                for f in files:
                    uploaded_file = TicketImage(file=f)
                    uploaded_file.save()
                    uploaded_file.ticket.add(ticket)
                for furl in url:
                    uploaded_url = TicketImage(external_url=furl)
                    uploaded_url.save()
                    uploaded_url.ticket.add(ticket)
            else:
                ticket_one = self.model(manifest_num=f'{form.cleaned_data["manifest"]}',
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
                ticket_two = self.model(manifest_num=f'{form.cleaned_data["manifest"]}',
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
                    uploaded_file = TicketImage(
                        file=f)
                    uploaded_file.save()
                    uploaded_file.ticket.add(ticket_one, ticket_two)
                for furl in url:
                    uploaded_url = TicketImage(
                        external_url=furl)
                    uploaded_url.save()
                    uploaded_url.ticket.add(ticket_one, ticket_two)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        manifest = self.request.GET.get('manifest', None)
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Ticket creation')
        if manifest is not None:
            rose_rocket_manifest_list = self.rose_rocket.get_active_manifests()  # list
            rose_rocket_dict = {m['full_id']: m for m in rose_rocket_manifest_list}
            manifest = f'MENCM{"".join([char for char in manifest if char.isdigit()])}'
            if manifest in rose_rocket_dict.keys():
                search_manifest = rose_rocket_dict[manifest]
                c_def['manifest_list'] = search_manifest['full_id']
            else:
                search_manifest = None
        chosen_man = self.request.GET.get('chosen_man', None)
        if chosen_man is not None:
            c_def['manifest_full_id'] = chosen_man
        return dict(list(context.items()) + list(c_def.items()))

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = super().get_initial()
        chosen_man = self.request.GET.get('chosen_man', None)

        if chosen_man is not None:
            rose_rocket_manifest_list = self.rose_rocket.get_active_manifests()  # list
            rose_rocket_dict = {m['full_id']: m for m in rose_rocket_manifest_list}
            chosen_manifest_id = rose_rocket_dict[chosen_man]['id']
            files = self.rose_rocket.get_manifest_files(chosen_manifest_id)
            initial['manifest'] = chosen_man
            if len(files.keys()) > 1:
                initial['consol'] = True
            common_list_for_files = []
            for files_list in [file_list for file_list in files.values()]:
                common_list_for_files.extend(files_list)
            initial['order_nums'] = ', '.join(list(files.keys()))
            initial['files_url'] = '  '.join([file for file in common_list_for_files if file is not None])
        return initial


class DeleteTicket(LoginRequiredMixin, View):
    login_url = 'login'
    next_page = 'next'
    form_class = DeleteForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            ticket = Tickets.objects.get(id=kwargs['tick_id'])
            ticket.status = 'Deleted'
            ticket.completed = datetime.datetime.now()
            ticket.save()
            return render(request, 'main/deleted.html', {'pk': kwargs['tick_id']})
        else:
            return HttpResponseForbidden


class WarehouseReplyFormView(LoginRequiredMixin, DataMixin, FormView):
    model = WarehouseReply
    login_url = 'login'
    next_page = 'next'
    template_name = 'main/warehouse_reply.html'
    success_url = '/warehouse/'
    form_class = WarehouseReplyForm

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('files')
        ticket = Tickets.objects.get(pk=self.kwargs['tick_id'])
        if form.is_valid():
            comments = form.cleaned_data['comments']
            reply = WarehouseReply(
                ticket=ticket,
                user=self.request.user,
                warehouse=Warehouses.objects.get(slug=self.kwargs['wh_slug']),
                comments=comments,
            )
            reply.save()
            for file in files:
                uploaded_file = ReplyImage(
                    file=file
                )
                uploaded_file.save()
                uploaded_file.reply.add(reply)
            ticket.status = 'Completed'
            ticket.completed = datetime.datetime.now()
            ticket.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Reply',
                                      wh_slug=self.kwargs['wh_slug'],
                                      tick_id=self.kwargs['tick_id']
                                      )
        return dict(list(context.items()) + list(c_def.items()))


# todo create view for completed tickets to show warehouse reply


class TripMonitor(LoginRequiredMixin, DataMixin, ListView):
    login_url = 'login'
    next_page = 'next'
    template_name = 'main/trip_monitor.html'
    # todo create reddis/celery automation update of loads from RR
    rose_rocket = RoseRocket()
