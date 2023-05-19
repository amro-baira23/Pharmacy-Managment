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

        pharmacy_id = self.user.pharmacy.id if self.user.pharmacy else None

        return {'type':self.user.get_roles(),'pharmacy_id':pharmacy_id,'tokens':tokens}