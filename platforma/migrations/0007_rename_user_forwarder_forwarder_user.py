# Generated by Django 4.1.1 on 2023-05-01 15:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('platforma', '0006_alter_forwarder_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='forwarder',
            old_name='user',
            new_name='forwarder_user',
        ),
    ]
