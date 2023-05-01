from .models import Distributor
from django import forms
from django.contrib.auth.models import User


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class DistributorUpdateForm(forms.ModelForm):
    class Meta:
        model = Distributor
        fields = ['company_name', 'address', 'about']
