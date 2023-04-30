from django.db import transaction
from django.contrib.auth import get_user_model

from rest_framework import serializers
from djoser.serializers import UserCreateSerializer

from .models import *


User = get_user_model()

# ########## COMPANY ##########

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id','name']

# ########## MEDICINE ##########

class MedicineListSerializer(serializers.ModelSerializer):
    company = serializers.StringRelatedField()
    class Meta:
        model = Medicine
        fields = [
            'id',
            'quantity',
            'price',
            'need_prescription',
            'is_expired',
            'brand_name',
            'barcode',
            'company',
            'type'
        ]
  

class MedicineCreateSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(max_length=50,write_only=True,required=False,allow_blank=True)
    substances = serializers.ListField(child=serializers.CharField(),max_length=50,required=False)
    class Meta:
        model = Medicine
        fields = [
            'id',
            'company_name',
            'brand_name',
            'barcode',
            'quantity',
            'price',
            'need_prescription',
            'expiry_date',
            'type',
            'substances'
        ]

    def validate_substances(self,sub):
        if len(set(sub)) != len(sub):
            raise serializers.ValidationError("cant have dublicate in this array")
        return sub 
    
    def validate_brand_name(self,name):
        return name.capitalize()
  
    def create(self, validated_data):
        name = validated_data.get('company_name')
        substances = validated_data.get('substances')
        ph_id = self.context['pharmacy_pk']
        company = None

        with transaction.atomic():
            if name:
                name = name.capitalize()
                validated_data.pop('company_name')
                company, created = Company.objects.get_or_create(pharmacy_id=ph_id,name=name)
            
            medicine , created = Medicine.unique_medicine.get_or_create(ph_id,company,validated_data)

            if not created:
                raise serializers.ValidationError({'error':'medicine with this data already exist'})
            
            if substances:
                validated_data.pop("substances")
                valid_subs = list(Substance.objects.filter(pharmacy_id=ph_id,name__in=substances))
            
                for sub in valid_subs:
                     if sub.name in substances:
                         substances.remove(sub.name)
            
                created_substances = [Substance.objects.create(name=name,pharmacy_id=ph_id) for name in substances]

                all_sub = created_substances + valid_subs

                final_subs = [MedicineSubstance(medicine=medicine,substance=sub) for sub in all_sub]
                MedicineSubstance.objects.bulk_create(final_subs)

            return medicine
        

class MedicineUpdateSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(max_length=50,write_only=True,required=False,allow_blank=True)
    class Meta:
        model = Medicine
        fields = [
            'brand_name',
            'barcode',
            'company_name',
            'type',
            'quantity',
            'price',
            'expiry_date',
            'need_prescription',
            'is_active'
        ]

    def validate_brand_name(self,name):
        return name.capitalize()
    
    def validate_company_name(self,company_name):
        return company_name.capitalize()

    def update(self, instance, validated_data):

        ph_id = self.context['pharmacy_pk']
        com_name = validated_data.get('company_name')
        company = instance.company if instance.company is not None and self.partial else None
        

        validated_data['barcode'] = validated_data.get('barcode') or instance.barcode
        validated_data['brand_name'] = validated_data.get('brand_name') or instance.brand_name
        validated_data['type'] = validated_data.get('type') or instance.type


        with transaction.atomic():

            if com_name is not None and com_name != '':
                company, created = Company.objects.get_or_create(pharmacy_id=ph_id,name=com_name)

            try:
                medicine = Medicine.unique_medicine.get(ph_id,company,validated_data)
                if medicine != instance:
                    raise serializers.ValidationError({'error':'cant update medicine , with same data already exist'})
            except Medicine.DoesNotExist:
                pass
            
            instance.company = company
            instance = super().update(instance, validated_data)
            return instance

# ########## SALEITEM ##########
    
class SaleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleItem
        fields = [
            'id',
            'medicine',
            'quantity',
            'price',
        ]

    def validate(self, attrs):
        medicine = attrs.get('medicine')
        if medicine.pharmacy.id != int(self.context['pharmacy_pk']):
            raise serializers.ValidationError('no medicine with such id for this pharmacy')
        return super().validate(attrs)

    
    def create(self, validated_data):
        medicine = validated_data['medicine']
        quantity = validated_data['quantity']
        with transaction.atomic():
            medicine.quantity -= quantity
            if medicine.quantity < 0:
                raise serializers.ValidationError({'error':f'not enough medicine {medicine.brand_name} in enventory'})
            medicine.save()
            return SaleItem.objects.create(sale=self.context['sale'],**validated_data)

# ########## SALE ##########

class SaleListSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(read_only=True)
    class Meta:
        model = Sale
        fields = [
            'id',
            'seller_name',
            'time',
        ]


class SaleSerizlizer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True)
    class Meta:
        model = Sale
        fields = ['id','seller_name','items','time']


class SaleCreateSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True)
    class Meta:
        model = Sale
        fields = ['items']


    def validate_items(self,items):
        if len(items) == 0:
            raise serializers.ValidationError('sale should have atleast one item')
        return items
    
    def save(self, **kwargs):
        self.instance = Sale.objects.create(pharmacy_id=self.context['pharmacy_pk'],seller_name=self.context['name'])
        return self.instance

# ########## PURCHASEITEM ##########

class PurchaseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseItem
        fields = ['id','medicine','quantity','price']

    def validate(self, attrs):
        medicine = attrs.get('medicine')
        if medicine.pharmacy.id != int(self.context['pharmacy_pk']):
            raise serializers.ValidationError('no medicine with such id for this pharmacy')
        return super().validate(attrs)
    
    def create(self, validated_data):
        medicine = validated_data['medicine']
        quantity = validated_data['quantity']
        with transaction.atomic():
            medicine.quantity += quantity
            medicine.save()
            return PurchaseItem.objects.create(purchase=self.context['purchase'],**validated_data)

# ########## PURCHASE ##########

class PurchaseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = [
            'id',
            'reciver_name',
            'time'
        ]
    

class PurchaseSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(many=True)
    class Meta:
        model = Purchase
        fields = [
            'id',
            'reciver_name',
            'time',
            'items'
        ]
    

class PurchaseCreateSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(many=True)
    class Meta:
        model = Purchase
        fields = ['items']

    def validate_items(self,items):
        if len(items) == 0:
            raise serializers.ValidationError('sale should have atleast one item')
        return items

    def save(self, **kwargs):
        self.instance = Purchase.objects.create(reciver_name=self.context['name'],pharmacy_id=self.context['pharmacy_pk'])
        return self.instance
    
# ########## PHARMACY ##########

class PharmacyListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Pharmacy
        fields = ['id','name']


class PharmacySerializer(serializers.ModelSerializer):

    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Pharmacy
        fields = ['owner','name','city','street','phone_number']

    
    def create(self, validated_data):
        return Pharmacy.objects.create(owner_id=self.context['owner_id'],**validated_data)
    
# ########## EMPLOYEE ##########

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