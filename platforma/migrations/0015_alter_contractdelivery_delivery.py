# Generated by Django 4.1.1 on 2023-05-02 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('platforma', '0014_contractdelivery'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contractdelivery',
            name='delivery',
            field=models.CharField(choices=[('ee', 'Economy express'), ('ed', 'Express delivery'), ('dp', 'Drop off/pick up points')], help_text='Freight service', max_length=2, verbose_name='Delivery'),
        ),
    ]
