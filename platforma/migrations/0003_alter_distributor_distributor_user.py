# Generated by Django 4.1.1 on 2023-04-30 17:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('platforma', '0002_alter_hstariff_tariff_rate_distributor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='distributor',
            name='distributor_user',
            field=models.OneToOneField(limit_choices_to={'groups__name': 'distributor'}, on_delete=django.db.models.deletion.CASCADE, related_name='distributor', to=settings.AUTH_USER_MODEL),
        ),
    ]
