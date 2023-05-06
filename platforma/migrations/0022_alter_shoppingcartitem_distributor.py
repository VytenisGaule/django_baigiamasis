# Generated by Django 4.1.1 on 2023-05-03 09:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('platforma', '0021_alter_shoppingcartitem_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shoppingcartitem',
            name='distributor',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='platforma.distributor'),
        ),
    ]