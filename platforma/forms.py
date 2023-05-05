from .models import Distributor, Forwarder, Customer, ShoppingCartItem, ContractDelivery
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


class CartDeliveryForm(forms.Form):
    delivery_type = forms.ChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        distributor_id = kwargs.pop('distributor_id')
        super().__init__(*args, **kwargs)
        contract_delivery_choices = ContractDelivery.objects.filter(distributor_id=distributor_id).values_list('delivery', 'delivery')
        self.fields['delivery_type'].choices = contract_delivery_choices


class ShoppingCartItemForm(forms.ModelForm):
    class Meta:
        model = ShoppingCartItem
        fields = ['quantity']
