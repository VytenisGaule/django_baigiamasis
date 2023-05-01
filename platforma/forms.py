from .models import Distributor, Forwarder, Customer
from django import forms
from django.contrib.auth.models import User


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': 'Nickname',
        }


class DistributorUpdateForm(forms.ModelForm):
    class Meta:
        model = Distributor
        fields = ['company_name', 'registration_code', 'address', 'about', 'avatar']


class ForwarderUpdateForm(forms.ModelForm):
    class Meta:
        model = Forwarder
        fields = ['company_name', 'registration_code', 'address', 'about', 'avatar']


class CustomerUpdateForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'address', 'region', 'avatar']
        labels = {
            'name': 'First Name and Last Name (or Company Name)',
        }
