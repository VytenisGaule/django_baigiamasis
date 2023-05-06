# Generated by Django 4.1.1 on 2023-04-28 13:56

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HScode',
            fields=[
                ('hs_code', models.CharField(help_text='HS code must contain exactly 10 digits', max_length=10, primary_key=True, serialize=False, validators=[django.core.validators.RegexValidator(regex='^\\d{10}$')])),
                ('hs_description', models.TextField(blank=True, help_text='Name of HS tariff', max_length=1000, null=True, verbose_name='Description')),
                ('hs_detailed', models.TextField(blank=True, help_text='HS tariff explained', max_length=1000, null=True, verbose_name='Self-explanatory texts')),
            ],
            options={
                'ordering': ['hs_code', 'hs_description'],
            },
        ),
        migrations.CreateModel(
            name='Origin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('origin_code', models.CharField(help_text='GB - United Kingdom, US, etc', max_length=5, verbose_name='Origin code')),
                ('origin_name', models.CharField(help_text='Country, group, or arrangement', max_length=100, verbose_name='Origin')),
            ],
            options={
                'ordering': ['origin_code', 'origin_name'],
            },
        ),
        migrations.CreateModel(
            name='HSTariff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tariff_rate', models.DecimalField(decimal_places=2, help_text='Tariff rate for the HS code and origin', max_digits=5)),
                ('legal_base', models.CharField(help_text='EU regulation link', max_length=100, verbose_name='Legal base')),
                ('hs_code_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='platforma.hscode')),
                ('origin_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='platforma.origin')),
            ],
            options={
                'ordering': ['hs_code_id', 'origin_id'],
                'unique_together': {('origin_id', 'hs_code_id')},
            },
        ),
    ]