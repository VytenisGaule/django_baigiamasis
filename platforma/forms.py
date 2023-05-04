from .models import Distributor, Forwarder, Customer, ShoppingCart, ShoppingCartItem
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


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


class ShoppingCartForm(forms.ModelForm):
    cart_delivery_type = forms.CharField(required=False)

    class Meta:
        model = ShoppingCart
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            self.fields['cart_delivery_type'].initial = instance.cart_delivery_type


class ShoppingCartItemForm(forms.ModelForm):
    class Meta:
        model = ShoppingCartItem
        fields = ['quantity']
