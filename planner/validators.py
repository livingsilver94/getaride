import datetime

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def validate_adult(birth_date):
    today = datetime.date.today()
    age = today.year - birth_date.year
    age -= (birth_date.month, birth_date.day) < (today.month, today.day)
    if age < 18:
        raise ValidationError(_('You must be at least 18 to sign up'))
