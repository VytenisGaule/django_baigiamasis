# Generated by Django 4.1.1 on 2023-05-04 23:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('platforma', '0025_alter_shoppingcart_distributor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contractdelivery',
            name='delivery',
            field=models.CharField(choices=[('ee', 'Economy express'), ('ed', 'Express delivery'), ('dp', 'Drop off/pick up')], help_text='Freight service', max_length=2, verbose_name='Delivery'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='region',
            field=models.CharField(blank=True, choices=[('ce', 'Bulgaria, Czech Republic, Romania, Slovakia'), ('ne', 'Denmark, Finland, Ireland, Sweden'), ('se', 'Croatia, Greece, Italy, Portugal, Spain'), ('we', 'Austria, Belgium, France, Germany, Netherlands, Switzerland'), ('ee', 'Estonia, Latvia, Lithuania, Poland')], default='Northern Europe', help_text='Location of customer to determine delivery expences', max_length=20, verbose_name='Region'),
        ),
    ]