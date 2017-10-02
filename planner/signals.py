from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from .models import Step


@receiver(m2m_changed, sender=Step.passengers.through)
def check_passengers(sender, **kwargs):
    step = kwargs['instance']
    if step.passengers.count() >= 8:
        raise ValidationError(_("You exceeded passenger maximum number"))
