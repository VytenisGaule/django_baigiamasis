# Generated by Django 4.1.1 on 2023-05-02 12:39

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('platforma', '0012_alter_customer_region_item'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='gross_weight',
            field=models.DecimalField(decimal_places=3, default=Decimal('0.000'), max_digits=6, verbose_name='NetWeight'),
        ),
        migrations.AddField(
            model_name='item',
            name='net_weight',
            field=models.DecimalField(decimal_places=3, default=Decimal('0.000'), max_digits=6, verbose_name='NetWeight'),
        ),
        migrations.AddField(
            model_name='item',
            name='volume',
            field=models.DecimalField(decimal_places=5, default=Decimal('0.00000'), max_digits=6, verbose_name='Volume'),
        ),
    ]