from django.db import transaction
from django.contrib.auth import get_user_model

from rest_framework import serializers
from djoser.serializers import UserCreateSerializer

from .models import *

User = get_user_model()

class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = [
            'id',
            'brand_name',
            'company',
            'barcode',
            'type',
            'quantity',
            'price',
        ]

class PurchaseSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Purchase
        fields = [
            'id',
            'reciver_name',
            'items'
        ]
    
    def get_items(self,obj):
        if hasattr(obj,'id'):
            print(obj)
            pk = obj.pk
            items = PurchaseItem.objects.filter(purchase_id=pk)
            arr = []
            for item in items:
                item = PurchaseItemSerializer(item).data
                arr.append(item)
            return arr
        return None
class PurchaseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseItem
        fields = [
            'medicine',
            'purchase',
            'quantity',
            'price',
        ]


class PharmacyListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Pharmacy
        fields = ['id','name']


    def to_representation(self, instance):
        return super().to_representation(instance)

class PharmacySerializer(serializers.ModelSerializer):

    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Pharmacy
        fields = ['owner','name','city','street','phone_number']

    
    def create(self, validated_data):
        return Pharmacy.objects.create(owner_id=self.context['owner_id'],**validated_data)
    

class EmployeeListSerializer(serializers.ModelSerializer):

    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Employee
        fields = ['id','user','role']


class EmployeeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    pharmacy = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Employee
        fields = ['pharmacy','user','role','phone_number','salry']


class EmployeeCreateSerializer(UserCreateSerializer):
    role = serializers.CharField(max_length=1,default=EMPLOYEE,write_only=True)
    phone_number = serializers.CharField(max_length=10,write_only=True)
    salry = serializers.IntegerField(write_only=True,min_value=0)
    class Meta(UserCreateSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields + ('role','phone_number','salry')

    def validate(self, attrs): 
        data = {}
        data['role'] = attrs.get('role')  
        data['salry']= attrs.get('salry')
        data['phone_number'] = attrs.get('phone_number')
        data['pharmacy_id'] = self.context['pharmacy_pk']

        serializer = EmployeeSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        data = {}
        data['first_name'] = attrs.get('first_name')  
        data['last_name']= attrs.get('last_name')
        data['email'] = attrs.get('email')
        data['password'] = attrs.get('password')

        super().validate(data)
        
        return attrs

    def save(self, **kwargs):
        data = {}
        data['first_name'] = self.validated_data.pop('first_name')  
        data['last_name']= self.validated_data.pop('last_name')
        data['email'] = self.validated_data.pop('email')
        data['password'] = self.validated_data.pop('password')

        with transaction.atomic():
            self.instance = self.create(data)
            Employee.objects.create(pharmacy_id=self.context['pharmacy_pk'],user=self.instance,**self.validated_data)

            return self.instance


