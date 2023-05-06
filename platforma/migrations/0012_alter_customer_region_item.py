# Generated by Django 4.1.1 on 2023-05-02 07:59

from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('platforma', '0011_alter_customer_region'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='region',
            field=models.CharField(blank=True, choices=[('Central Europe', 'Bulgaria, Czech Republic, Romania, Slovakia'), ('Northern Europe', 'Denmark, Finland, Ireland, Sweden'), ('Southern Europe', 'Croatia, Greece, Italy, Portugal, Spain'), ('Western Europe', 'Austria, Belgium, France, Germany, Netherlands, Switzerland'), ('Eastern Europe', 'Estonia, Latvia, Lithuania, Poland')], default='Northern Europe', help_text='Location of customer to determine delivery expences', max_length=20, verbose_name='Region'),
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('description', models.CharField(help_text='Short description', max_length=1000, verbose_name='Description')),
                ('photo', models.ImageField(default='photos/no_image.png', upload_to='photos', verbose_name='Photo')),
                ('price', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5, verbose_name='Price')),
                ('distributor_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='platforma.distributor')),
                ('hs_tariff_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='platforma.hstariff')),
            ],
            options={
                'ordering': ['distributor_id', 'name'],
            },
        ),
    ]