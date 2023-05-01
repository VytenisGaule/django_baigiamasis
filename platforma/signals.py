from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from django.conf import settings
from .models import Distributor, Forwarder, Customer


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        group = Group.objects.get(name='customer')
        instance.groups.add(group)


@receiver(m2m_changed, sender=User.groups.through)
def update_distributor(sender, instance, action, model, **kwargs):
    if action == 'post_add' and model == Group and 'distributor' in Group.objects.filter(
            pk__in=kwargs['pk_set']).values_list('name', flat=True):
        Distributor.objects.get_or_create(distributor_user=instance)
        print('created as distributor')
    elif action == 'post_remove' and model == Group and not instance.groups.filter(name='distributor').exists():
        try:
            distributor = instance.distributor
            distributor.delete()
            print('removed from distributor')
        except Distributor.DoesNotExist:
            pass


@receiver(m2m_changed, sender=User.groups.through)
def update_forwarder(sender, instance, action, model, **kwargs):
    if action == 'post_add' and model == Group and 'forwarder' in Group.objects.filter(
            pk__in=kwargs['pk_set']).values_list('name', flat=True):
        Forwarder.objects.get_or_create(forwarder_user=instance)
        print('created as forwarder')
    elif action == 'post_remove' and model == Group and not instance.groups.filter(name='forwarder').exists():
        try:
            forwarder = instance.forwarder
            forwarder.delete()
            print('removed from forwarder')
        except Forwarder.DoesNotExist:
            pass


@receiver(m2m_changed, sender=User.groups.through)
def update_customer(sender, instance, action, model, **kwargs):
    if action == 'post_add' and model == Group and 'customer' in Group.objects.filter(
            pk__in=kwargs['pk_set']).values_list('name', flat=True):
        Customer.objects.get_or_create(customer_user=instance)
        print('created as customer')
    elif action == 'post_remove' and model == Group and not instance.groups.filter(name='customer').exists():
        try:
            customer = instance.customer
            customer.delete()
            print('removed from customer')
        except Customer.DoesNotExist:
            pass
