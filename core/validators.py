from django.core.exceptions import ValidationError
from datetime import datetime
from django.utils.translation import gettext as _

def validate_old_date(date):
    now = datetime.now().date()
    if now > date:
        raise ValidationError(_('you must enter a date in the present'))
