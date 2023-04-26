from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from core.models import Employee,Pharmacy


class MyTokenObtain(TokenObtainPairSerializer):

    def validate(self, attrs):
        tokens = super().validate(attrs)
        if self.user.is_owner:
            ph = Pharmacy.objects.filter(owner_id=self.user.id)
            type = 'O'
            pharmacy_id = ph.id if ph.exists() else None
        else :
            type = None

        if not type:     
            try:
                em = Employee.objects.get(user_id=self.user.id)
                pharmacy_id = em.pharmacy.id
                type = em.role
            except Employee.DoesNotExist:
                raise serializers.ValidationError('undifained user type')

        return {'type':type,'pharmacy_id':pharmacy_id,'tokens':tokens}