import uuid
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import RegexValidator
from datetime import date
from tinymce.models import HTMLField
from PIL import Image


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
    tariff_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Tariff rate for the HS code and origin")
    legal_base = models.CharField('Legal base', max_length=100, help_text='EU regulation link')

    class Meta:
        unique_together = ['origin_id', 'hs_code_id']
        ordering = ['hs_code_id', 'origin_id']

    def __str__(self):
        return f'{self.tariff_rate}'
