from django.utils.translation import gettext as _

from rest_framework import exceptions
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from core.models import UserRole

from djoser.conf import settings

class MyTokenObtain(TokenObtainPairSerializer):

    default_error_messages = {
        "no_active_account": settings.CONSTANTS.messages.INVALID_CREDENTIALS_ERROR,
        'undifained user type': _('undifained user type'),
    }

    def validate(self, attrs):
        tokens = super().validate(attrs)

        if self.user.is_staff:
            raise exceptions.NotAcceptable(self.error_messages["undifained user type"],"undifained user type",)

        roles = UserRole.objects.filter(user=self.user).values_list('role',flat=True)

        if 'manager' in roles:
            type = 'M'
        elif 'pharmacy_manager' in roles:
            type = 'PM'
        elif 'saller' in roles and 'purcher' in roles:
            type = 'PS'
        elif 'saller' in roles:
            type = 'S'
        elif 'purcher' in roles:
            type = 'P'        
                

        pharmacy_id = self.user.pharmacy.id if self.user.pharmacy else None

        return {'type':type,'pharmacy_id':pharmacy_id,'tokens':tokens}