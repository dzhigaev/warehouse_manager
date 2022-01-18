from django import forms
from .models import Warehouses, Tickets, Trucks, Trailers


class MyLogin(forms.Form):
    username = forms.CharField(max_length=10, label='Login', required=True)
    password = forms.CharField(max_length=100, label='Password', required=True)


class ManifestSearch(forms.Form):
    manifest = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={'id': 'manifest1'},
        ),
        # max_digits=6,
        label='MENCM:',
        required=True)


class TripCreation(forms.Form):
    manifest = forms.CharField(widget=forms.NumberInput(attrs={'id':'manifest'}),
                               max_length=11, label='MENCM', required=False)
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
    # type_of_load = forms.ChoiceField(choices=[(0, 'Consolidated'), (1, 'Dedicated'), (2, 'Special')])
    consol = forms.BooleanField(required=False, help_text='If trailer going to be consolidated mark this checkmark')

    # created = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'hidden'},
    #                                                          format='MM-DD-YYYY HH:mm')) #todo add js for automatic time insert?
    files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)
    incoming_instructions = forms.CharField(widget=forms.Textarea, required=False)
    outgoing_instructions = forms.CharField(widget=forms.Textarea, required=False)
    # user = forms.CharField(widget=forms.TextInput(attrs={'type': 'hidden'}))
    # manifest.widget.attrs['class'] = 'primary-btn'
