from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from core.models import Employee,Pharmacy


class MyTokenObtain(TokenObtainPairSerializer):

    def validate(self, attrs):
        tokens = super().validate(attrs)

        type = 'O' if Pharmacy.objects.filter(owner__id=self.user.id).exists() else None

        if not type:     
            try:
                type = Employee.objects.get(user_id=self.user.id).role
                print(type)
            except Employee.DoesNotExist:
                raise serializers.ValidationError('undifained user type')

        return {'type':type,'tokens':tokens}