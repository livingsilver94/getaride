from django.db import IntegrityError
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from planner.models import Step


@receiver(m2m_changed, sender=Step.passengers.through)
def can_join_trip(sender, **kwargs):
    if kwargs['action'] == 'pre_add':
        inst = kwargs['instance']
        if inst.passengers__count >= inst.trip__max_num_passengers:
            raise IntegrityError
