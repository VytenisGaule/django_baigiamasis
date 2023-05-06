# Generated by Django 4.1.1 on 2023-05-03 08:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('platforma', '0019_shoppingcartitem'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shoppingcart',
            name='items',
        ),
        migrations.AlterField(
            model_name='shoppingcartitem',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='platforma.item'),
        ),
        migrations.AlterField(
            model_name='shoppingcartitem',
            name='quantity',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterUniqueTogether(
            name='shoppingcartitem',
            unique_together={('cart', 'item')},
        ),
    ]
