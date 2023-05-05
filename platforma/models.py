import uuid
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import RegexValidator
from datetime import datetime
from tinymce.models import HTMLField
from PIL import Image
from decimal import Decimal


# Create your models here.


class Origin(models.Model):
    origin_code = models.CharField('Origin code', max_length=5, help_text='GB - United Kingdom, US, etc')
    origin_name = models.CharField('Origin', max_length=100, help_text='Country, group, or arrangement')

    class Meta:
        ordering = ['origin_code', 'origin_name']

    def __str__(self):
        return f'{self.origin_name} ({self.origin_code})'


class HScode(models.Model):
    hs_code = models.CharField(primary_key=True, max_length=10, validators=[RegexValidator(regex=r'^\d{10}$')],
                               help_text="HS code must contain exactly 10 digits")
    hs_description = models.TextField('Description', max_length=1000, null=True, blank=True,
                                      help_text='Name of HS tariff')
    hs_detailed = models.TextField('Self-explanatory texts', max_length=1000, null=True, blank=True,
                                   help_text='HS tariff explained')

    class Meta:
        ordering = ['hs_code', 'hs_description']

    def __str__(self):
        return f'{self.hs_code}'


class HSTariff(models.Model):
    origin_id = models.ForeignKey(Origin, on_delete=models.CASCADE)
    hs_code_id = models.ForeignKey(HScode, on_delete=models.CASCADE)
    tariff_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Tariff rate of HS code and origin")
    legal_base = models.CharField('Legal base', max_length=100, help_text='EU regulation link')

    class Meta:
        unique_together = ['origin_id', 'hs_code_id']
        ordering = ['hs_code_id', 'origin_id']

    def __str__(self):
        return f'{self.hs_code_id}, {self.origin_id.origin_code} - {self.tariff_rate}%'


class Distributor(models.Model):
    distributor_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='distributor',
                                            limit_choices_to={'groups__name': 'distributor'})
    avatar = models.ImageField(default='profile_pics/default.png', upload_to='profile_pics')
    company_name = models.CharField(max_length=255)
    registration_code = models.CharField(max_length=20, default='')
    address = models.CharField(max_length=1000)
    about = models.CharField(max_length=1000, null=True, blank=True)

    class Meta:
        ordering = ['company_name']
        permissions = [
            ('can_edit_items', 'Can edit owned items'),
        ]

    def __str__(self):
        return f'{self.company_name}'


class Item(models.Model):
    name = models.CharField('Name', max_length=100)
    description = models.CharField('Description', max_length=1000, help_text='Short description')
    photo = models.ImageField('Photo', upload_to="photos", default='photos/no_image.png')
    price = models.DecimalField('Price', default=Decimal('0.00'), max_digits=5, decimal_places=2)
    net_weight = models.DecimalField('Net Weight', default=Decimal('0.000'), max_digits=6, decimal_places=3)
    gross_weight = models.DecimalField('Gross Weight', default=Decimal('0.000'), max_digits=6, decimal_places=3)
    volume = models.DecimalField('Volume', default=Decimal('0.00000'), max_digits=6, decimal_places=5)
    hs_tariff_id = models.ForeignKey(HSTariff, on_delete=models.PROTECT)
    distributor = models.ForeignKey(Distributor, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['distributor', 'name']

    def __str__(self):
        return f'{self.name}, {self.price} EUR'


class Forwarder(models.Model):
    forwarder_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='forwarder',
                                          limit_choices_to={'groups__name': 'forwarder'})
    avatar = models.ImageField(default='profile_pics/default.png', upload_to='profile_pics')
    company_name = models.CharField(max_length=255)
    registration_code = models.CharField(max_length=20, default='')
    address = models.CharField(max_length=1000)
    about = models.CharField(max_length=1000, null=True, blank=True)

    class Meta:
        ordering = ['company_name']
        permissions = [
            ('can_edit_packages', 'Can edit owned packages'),
        ]

    def __str__(self):
        return f'{self.company_name}'


class ContractDelivery(models.Model):
    DELIVERY_TYPES = (
        ('ee', 'Economy express'),
        ('ed', 'Express delivery'),
        ('dp', 'Drop off/pick up')
    )
    delivery = models.CharField("Delivery", max_length=2, choices=DELIVERY_TYPES, help_text='Freight service')
    DELIVERY_REGION_LOCATION = (
        ('ce', 'Central Europe'),
        ('ne', 'Northern Europe'),
        ('se', 'Southern Europe'),
        ('we', 'Western Europe'),
        ('ee', 'Eastern Europe')
    )
    region = models.CharField("Region", max_length=2, choices=DELIVERY_REGION_LOCATION, help_text='Delivery location')
    freight_cost_vkg = models.DecimalField('Freight cost v/kg', default=Decimal('0.00'), max_digits=4, decimal_places=2,
                                           help_text='Cheargable weight or volume, whatever is bigger')
    distributor_id = models.ForeignKey(Distributor, on_delete=models.CASCADE)
    forwarder_id = models.ForeignKey(Forwarder, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.freight_cost_vkg}'


class Customer(models.Model):
    customer_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer',
                                         limit_choices_to={'groups__name': 'customer'})
    avatar = models.ImageField(default='profile_pics/default.png', upload_to='profile_pics')
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=1000)

    LOCATION_REGION = (
        ('ce', 'Bulgaria, Czech Republic, Romania, Slovakia'),
        ('ne', 'Denmark, Finland, Ireland, Sweden'),
        ('se', 'Croatia, Greece, Italy, Portugal, Spain'),
        ('we', 'Austria, Belgium, France, Germany, Netherlands, Switzerland'),
        ('ee', 'Estonia, Latvia, Lithuania, Poland')
    )

    region = models.CharField(
        "Region",
        max_length=20,
        choices=LOCATION_REGION,
        blank=True,
        default='Northern Europe',
        help_text='Location of customer to determine delivery expences'
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name}'


class ShoppingCart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    distributor = models.ForeignKey(Distributor, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    cart_delivery_type = models.CharField(max_length=2, blank=True)

    def __str__(self):
        return f'{self.customer} - {self.distributor}'

    @property
    def total_items(self):
        return sum(item_obj.quantity for item_obj in self.shoppingcartitem_set.all())

    @property
    def items_price(self):
        return sum(item_obj.subtotal for item_obj in self.shoppingcartitem_set.all())

    @property
    def delivery_weight(self):
        return sum(item_obj.weight for item_obj in self.shoppingcartitem_set.all())

    @property
    def delivery_price(self):
        if not self.cart_delivery_type or not self.delivery_weight:
            return None

        contract_delivery = ContractDelivery.objects.filter(
            distributor_id=self.distributor.id,
            region=self.customer.region,
            delivery=self.cart_delivery_type
        ).first()

        if not contract_delivery:
            return None

        freight_cost = round(self.delivery_weight * contract_delivery.freight_cost_vkg, 2)
        return freight_cost


class ShoppingCartItem(models.Model):
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'item')

    @property
    def subtotal(self):
        return self.item.price * self.quantity

    # noinspection PyTypeChecker
    @property
    def weight(self):
        gross_weight = self.item.gross_weight
        volume = self.item.volume
        if gross_weight and volume:
            return max(gross_weight, volume * 1000) * self.quantity
        elif gross_weight:
            return gross_weight * self.quantity
        elif volume:
            return volume * 1000 * self.quantity
        else:
            return 0
