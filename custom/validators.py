from django.core.exceptions import ValidationError

def validate_hotmail_or_gmail_email(email):
    if not email.endswith("@gmail.com") and not email.endswith("@hotmail.com"):
        raise ValidationError('only hotmail or gmail email types are allowd')
