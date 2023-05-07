from .models import Distributor, Forwarder, Customer, ShoppingCartItem, ContractDelivery, Item
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
        contract_delivery_choices = ContractDelivery.objects.filter(distributor_id=distributor_id).values_list(
            'delivery', 'delivery')
        self.fields['delivery_type'].choices = contract_delivery_choices


class ShoppingCartItemForm(forms.ModelForm):
    class Meta:
        model = ShoppingCartItem
        fields = ['quantity']


class DistributorItemCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        """Distributorius prekės kortelėje priskiriamas prisijungusiam vartotojui"""
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['distributor'].initial = user.distributor

    class Meta:
        model = Item
        fields = ['name', 'description', 'photo', 'price', 'net_weight', 'gross_weight', 'volume', 'hs_tariff_id',
                  'distributor']
        widgets = {'hs_tariff_id': forms.TextInput(attrs={'class': 'vForeignKeyRawIdAdmin'}),
                   'distributor': forms.HiddenInput()
                   }
        raw_id_fields = ('hs_tariff_id',)


class PaymentForm(forms.Form):
    confirm_purchase = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='I do purchase and pay for the items in my shopping cart.'
    )
