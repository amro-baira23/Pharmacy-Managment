from django.db import transaction
from django.contrib.auth import get_user_model

from rest_framework import serializers
from djoser.serializers import UserCreateSerializer

from .models import *

User = get_user_model()

class MedicineSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(max_length=50,write_only=True,required=False)
    company = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Medicine
        fields = [
            'id',
            'brand_name',
            'company',
            'barcode',
            'company_name',
            'type',
            'quantity',
            'price',
            'expiry_date',
            'need_prescription'
        ]

    def create(self, validated_data):
        return super().create(validated_data)

    def create(self, validated_data):
        name = validated_data.get('company_name')
        ph_id = self.context['pharmacy_pk']
        company = None

        with transaction.atomic():
            if name:
                validated_data.pop('company_name')
                try:
                    company = Company.objects.get(pharmacy_id=ph_id,name=name)
                except Company.DoesNotExist:
                    company = Company.objects.create(pharmacy_id=ph_id,name=name)
            if company is not None:
                try:
                    medicine = Medicine.unique_medicine.get_comp(ph_id,company.id,validated_data)
                except Medicine.DoesNotExist:
                    medicine = Medicine.objects.create(pharmacy_id=ph_id,**validated_data,company_id=company.id)
            else:
                try:
                    medicine = Medicine.unique_medicine.get(ph_id,validated_data)
                except Medicine.DoesNotExist:
                    medicine = Medicine.objects.create(pharmacy_id=ph_id,**validated_data)

            return medicine
        
    def update(self, instance, validated_data):
        ph_id = self.context['pharmacy_pk']
        try:
            Medicine.unique_medicine.get(ph_id,validated_data)
            raise serializers.ValidationError({'error':'medicine with this data already exist'})
        except Medicine.DoesNotExist:
            return super().update(instance, validated_data)    
                        

class PurchaseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = [
            'id',
            'reciver_name',
            'time_stamp'
        ]
    
class SaleSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Sale
        fields = [
            'id',
            'seller_name',
            'time_stamp',
            'items'
        ]
    
    def get_items(self,obj):
        items = SaleItem.objects.filter(sale_id=obj.id)
        items = SaleItemSerializer(items,many=True).data
        return items
    
class SaleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleItem
        fields = [
            'medicine',
            'quantity',
            'price',
        ]

    def validate(self, attrs):
        medicine = attrs['medicine']
        sale = self.context.get('sale')
        if not medicine.pharmacy.id is sale.pharmacy.id:
            raise serializers.ValidationError({'message':'unauthorized operation'})
        return super().validate(attrs)
    
    def create(self, validated_data):
        medicine = validated_data['medicine']
        quantity = validated_data['quantity']
        medicine.quantity -= quantity
        medicine.save()
        return super().create(validated_data)

class PurchaseSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Purchase
        fields = [
            'id',
            'reciver_name',
            'time_stamp',
            'items'
        ]
    
    def get_items(self,obj):
        items = PurchaseItem.objects.filter(purchase_id=obj.id)
        items = PurchaseItemSerializer(items,many=True).data
        return items

class PurchaseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseItem
        fields = [
            'medicine',
            'quantity',
            'price',
        ]

    def validate(self, attrs):
        medicine = attrs['medicine']
        purchase = self.context.get('purchase')
        if not medicine.pharmacy.id is purchase.pharmacy.id:
            raise serializers.ValidationError({'message':'unauthorized operation'})
        return super().validate(attrs)
    
    def create(self, validated_data):
        medicine = validated_data['medicine']
        quantity = validated_data['quantity']
        medicine.quantity += quantity
        medicine.save()
        return super().create(validated_data)

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


