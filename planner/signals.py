from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Step


@receiver(m2m_changed, sender=Step.passengers.through)
def check_passengers(sender, **kwargs):
    step = kwargs['instance']
    if kwargs['action'] == 'post_add':
        if step.passengers.count() >= step.trip.max_num_passengers:
            step.trip.is_joinable = False
    elif kwargs['action'] == 'post_remove':
        step.trip.is_joinable = True
