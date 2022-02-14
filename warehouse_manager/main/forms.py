from django import forms
from .models import Warehouses, Trucks, Trailers, WarehouseReply


class MyLogin(forms.Form):
    username = forms.CharField(max_length=10, label='Login', required=True)
    password = forms.CharField(max_length=100, label='Password', required=True)


class TripCreation(forms.Form):
    manifest = forms.CharField(widget=forms.TextInput(attrs={'id': 'manifest', 'type': 'hidden'}),
                               max_length=11,
                               label='',
                               required=False)
    outgoing = forms.ModelChoiceField(queryset=Warehouses.objects.all())
    outgoing_due_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'},
                                                                       format='MM-DD-YYYY HH:mm'),
                                            input_formats=['%Y-%m-%d %HH:%M'],
                                            required=True,
                                            label='Outgoing ticket due time')
    incoming = forms.ModelChoiceField(queryset=Warehouses.objects.all())
    incoming_due_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'},
                                                                       format='MM-DD-YYYY HH:mm'),
                                            input_formats=['%Y-%m-%d %HH:%M'],
                                            required=True,
                                            label='Outgoing ticket due time')

    order_nums = forms.CharField(widget=forms.Textarea, required=False)
    truck = forms.ModelChoiceField(queryset=Trucks.objects.all(), required=False)
    trailer = forms.ModelChoiceField(queryset=Trailers.objects.all(), required=False)
    consol = forms.BooleanField(required=False, help_text='If trailer going to be consolidated mark this checkmark')

    files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)
    files_url = forms.URLField(widget=forms.URLInput(attrs={'multiple': True}), required=False)
    incoming_instructions = forms.CharField(widget=forms.Textarea, required=False)
    outgoing_instructions = forms.CharField(widget=forms.Textarea, required=False)


class WarehouseReplyForm(forms.Form):
    comments = forms.CharField(widget=forms.Textarea, required=False)
    files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)

class DeleteForm(forms.Form):
    pass


