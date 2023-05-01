from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from .models import Distributor


@receiver(m2m_changed, sender=User.groups.through)
def update_distributor(sender, instance, action, model, **kwargs):
    if action == 'post_add' and model == Group and 'distributor' in Group.objects.filter(pk__in=kwargs['pk_set']).values_list('name', flat=True):
        Distributor.objects.get_or_create(distributor_user=instance)
        print('created as distributor')
    elif action == 'post_remove' and model == Group and not instance.groups.filter(name='distributor').exists():
        try:
            distributor = instance.distributor
            distributor.delete()
            print('removed from distributor')
        except Distributor.DoesNotExist:
            pass
