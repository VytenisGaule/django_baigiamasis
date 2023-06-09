import math
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import RegexValidator, MinValueValidator
from datetime import datetime
from tinymce.models import HTMLField
from PIL import Image
from decimal import Decimal


# Create your models here.


class Origin(models.Model):
    """Prekės kilmės šalis nurodoma etiketėje, nebūtinai sutampa su distributoriaus lokacija"""
    """Gali būti kad Filipinų distributorius parduoda Turkiškos kilmės prekę."""
    origin_code = models.CharField('Origin code', max_length=5, help_text='GB - United Kingdom, US, etc')
    origin_name = models.CharField('Origin', max_length=100, help_text='Country, group, or arrangement')

    class Meta:
        ordering = ['origin_code', 'origin_name']

    def __str__(self):
        return f'{self.origin_name} ({self.origin_code})'


class HScode(models.Model):
    """HS kodai - https://litarweb.lrmuitine.lt/taric/web/browsetariff_LT?Year=2023&Month=04&Day=23"""
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
    """Muito tarifas priklauso nuo HS kodo ir prekės kilmės šalies"""
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
    price = models.DecimalField('Price', default=Decimal('0.00'), max_digits=5, decimal_places=2,
                                validators=[MinValueValidator(Decimal('0.00'))])
    net_weight = models.DecimalField('Net Weight', default=Decimal('0.000'), max_digits=6, decimal_places=3,
                                     validators=[MinValueValidator(Decimal('0.00'))])
    gross_weight = models.DecimalField('Gross Weight', default=Decimal('0.000'), max_digits=6, decimal_places=3,
                                       validators=[MinValueValidator(Decimal('0.00'))])
    volume = models.DecimalField('Volume', default=Decimal('0.00000'), max_digits=6, decimal_places=5,
                                 validators=[MinValueValidator(Decimal('0.00'))])
    hs_tariff_id = models.ForeignKey(HSTariff, on_delete=models.PROTECT)
    distributor = models.ForeignKey(Distributor, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['distributor', 'name']

    def __str__(self):
        return f'{self.name}, {self.price} EUR'


class Forwarder(models.Model):
    """Ekspeditorius yra nebūtinai vežėjas. Įprastai ekspeditorius dirba su kryptimi (pvz. LT-UK auto, LT-DE air)"""
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
    """Skirtingi ekspeditoriai taiko skirtingas pristatymo paslaugas (skirtingi greičiai, metodai)
    Skirtingi vežėjai dirba skirtingomis kryptimis. Jei vežėjas neturi oro linijos iš Kanados į EU -
    tada jis nepasiųlys Kanados gamintojui 'ed' paslaugos"""
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
    """Nuo gyvvenamosios vietos regiono priklauso siuntų pristatymo kainos. Įsivaizduokime kad pvz.
    TNT turi siuntų paskirstymo terminalus Liege, arba Madride - ir ten paskirstomos siuntos iš JAV """
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

    """Transporto kaštų suma pagal kiekvienos prekės svorį arba tūrį krepšelyje"""
    """Pagal pristatymo būdą (pvz. nuo paštomato į paštomatą, arba nuo durų iki durų, ir pan.)"""
    """Ir gabenimo kainą iš gamintojo sandėlių iki konkretaus regiono, kuriame gyvena gavėjas"""

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

    """muito mokesčiu apmokestinamos tos siuntos, kurių vertė viršija 150 eur. Naujas 2022m EU reglamentas """
    """https://taxation-customs.ec.europa.eu/system/files/2022-11/Customs%20Guidance%20doc%20on%20LVC-Clean-20220915
    .pdf"""

    @property
    def duty(self):
        if self.items_price + self.delivery_price <= 150:
            return 0
        else:
            return sum(math.ceil(item_obj.item.price * item_obj.item.hs_tariff_id.tariff_rate / 100)
                       for item_obj in self.shoppingcartitem_set.all())


class ShoppingCartItem(models.Model):
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'item')

    @property
    def subtotal(self):
        return self.item.price * self.quantity

    """Siuntų kainą smulkių siuntų vežėjai įprastai skaičiuojama pagal tūrinį svorį."""
    """Pavyzdžiuis jei lengva siunta supakuota didelėje dėžėje - kainą lemia tūris, ne svoris"""

    # noinspection PyTypeChecker
    @property
    def weight(self):
        gross_weight = self.item.gross_weight
        volume = self.item.volume
        if gross_weight and volume:
            return max(gross_weight, volume * 200) * self.quantity
        elif gross_weight:
            return gross_weight * self.quantity
        elif volume:
            return volume * 200 * self.quantity
        else:
            return 0


class ShipmentManager(models.Manager):
    def at_location(self, location):
        return self.filter(location=location)


class Shipment(models.Model):
    total_price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    duty = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    date_created = models.DateTimeField(auto_now_add=True)
    invoice = models.FileField('Photo', upload_to="invoices", blank=True, null=True)
    distributor = models.ForeignKey(Distributor, on_delete=models.PROTECT)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    forwarder = models.ForeignKey(Forwarder, on_delete=models.PROTECT)

    LOCATION_CHOICES = (
        ('ad', 'At distributor'),
        ('cc', 'In colection couriers truck'),
        ('ct', 'In collection terminal'),
        ('sp', 'Shipping'),
        ('dt', 'In delivery terminal'),
        ('dc', 'In delivery couriers truck'),
    )

    location = models.CharField(choices=LOCATION_CHOICES, max_length=2, default='ad')
    objects = ShipmentManager()
