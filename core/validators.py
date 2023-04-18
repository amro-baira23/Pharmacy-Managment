from django.core.exceptions import ValidationError
from datetime import datetime

def validate_old_date(date):
    now = datetime.now().date()
    if now > date:
        raise ValidationError(f'you must enter a date in the present')
