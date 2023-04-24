from django.db import transaction
from django.contrib.auth import get_user_model

from rest_framework import serializers
from djoser.serializers import UserCreateSerializer

from .models import *


User = get_user_model()

class MedicineSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(max_length=50,write_only=True,required=False,allow_blank=True)
    company = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Medicine
        fields = [
            'id',
            'company_name',
            'company',
            'brand_name',
            'barcode',
            'quantity',
            'price',
            'need_prescription',
            'is_active',
            'expiry_date',
            'type'
        ]
  
    def create(self, validated_data):
        name = validated_data.get('company_name')
        ph_id = self.context['pharmacy_pk']
        company = None

        with transaction.atomic():
            if name:
                validated_data.pop('company_name')
                company, created = Company.objects.get_or_create(pharmacy_id=ph_id,name=name)

            
            medicine , created = Medicine.unique_medicine.get_or_create(ph_id,company,validated_data)

            if not created:
                raise serializers.ValidationError({'error':'medicine with this data already exist'})
            
            return medicine
        

class MedicineUpdateSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(max_length=50,write_only=True,required=False,allow_blank=True)
    company = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Medicine
        fields = [
            'company',
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

    def update(self, instance, validated_data):

        ph_id = self.context['pharmacy_pk']
        com_name = validated_data.get('company_name')
        company = instance.company if instance.company is not None and self.partial else None

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
    

class PurchaseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = [
            'id',
            'reciver_name',
            'time_stamp'
        ]
    
    
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


class SaleListSerializer(serializers.ModelSerializer):
    time = serializers.SerializerMethodField(read_only=True,method_name='format_time')
    seller_name = serializers.CharField(read_only=True)

    class Meta:
        model = Sale
        fields = [
            'id',
            'seller_name',
            'time',
        ]


    def format_time(self,sale):
        return sale.time_stamp.strftime(f"%Y-%m-%d %H:%m")
    

class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True,read_only=True)
    time = serializers.SerializerMethodField(read_only=True,method_name='format_time')
    seller_name = serializers.CharField(read_only=True)
    ids_list = serializers.ListField(child=serializers.IntegerField(min_value=0),write_only=True)
    amount_list = serializers.ListField(child=serializers.IntegerField(min_value=0),write_only=True)

    class Meta:
        model = Sale
        fields = [
            'id',
            'seller_name',
            'time',
            'items',
            'ids_list',
            'amount_list'
        ]

    def format_time(self,sale):
        return sale.time_stamp.strftime(f"%Y-%m-%d %H:%m")
    
    def validate(self, attrs):
        ids_length = len(attrs.get('ids_list'))
        amount_length = len(attrs.get('amount_list'))

        if ids_length != amount_length:
            raise serializers.ValidationError({'error':'ids_list and amount_list length must be equal'})
        
        if ids_length == 0:
            raise serializers.ValidationError({'error':'ids_list and amount_list length must gretter than 0'})

        return super().validate(attrs)
    
    def save(self, **kwargs):
        ids_list = self.validated_data.pop('ids_list')
        amount_list = self.validated_data.pop('amount_list')
        ids_set_length = len(set(ids_list))

        meds = Medicine.objects.filter(id__in=ids_list,pharmacy_id=self.context['pharmacy_pk'])

        if meds.count() != ids_set_length:
            raise serializers.ValidationError({'error':'some ids are invalid'})
        
        if ids_set_length != len(ids_list):
            for idx,i in enumerate(ids_list):
                if i != -1:
                    for idx2,j in enumerate(ids_list):
                        if idx != idx2 and i == j and i != -1:
                            amount_list[idx] += amount_list[idx2]
                            ids_list[idx2] = -1
                            amount_list[idx2] = -1

        with transaction.atomic():
            sale = Sale.objects.create(seller_name=self.context['name'],pharmacy_id=self.context['pharmacy_pk'])

            items = []

            for med in meds:
                idx = ids_list.index(med.id)
                qua = amount_list[idx]
                items.append(SaleItem(medicine=med,price=med.price,quantity=qua,sale=sale))
            
                med.quantity -= qua
                if med.quantity < 0:
                    raise serializers.ValidationError({'error':'not enough medicine to add to sale'})

            SaleItem.objects.bulk_create(items)
            Medicine.objects.bulk_update(meds,['quantity'])
        
        self.instance = sale
        return self.instance


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


