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
    price = serializers.IntegerField(read_only=True)
    class Meta:
        model = SaleItem
        fields = [
            'medicine',
            'quantity',
            'price',
        ]

    def validate(self, attrs):
        medicine = attrs.get('medicine')
        if medicine.pharmacy == None:
            raise serializers.ValidationError({'error':"no such medicne found"})
        if medicine.pharmacy.id != self.context['sale'].pharmacy.id:
            raise serializers.ValidationError({'error':'no medicine with such id for this pharmacy'})
        return super().validate(attrs)

    
    def create(self, validated_data):
        medicine = validated_data['medicine']
        quantity = validated_data['quantity']
        with transaction.atomic():
            medicine.quantity -= quantity
            if medicine.quantity <= 0:
                raise serializers.ValidationError({'error':'not enough medicine in enventory'})
            medicine.save()
            return SaleItem.objects.create(sale=self.context['sale'],price=medicine.price,**validated_data)


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

class SaleSerizlizer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True)
    class Meta:
        model = Sale
        fields = '__all__'


class SaleCreateSerializer(serializers.ModelSerializer):
    items = serializers.ListField(child=serializers.DictField(),write_only=True)
    class Meta:
        model = Sale
        fields = ['items']


    def validate_items(self,items):
        if len(items) == 0:
            raise serializers.ValidationError({'items':'sale should have atleast one item'})
        return items

    def save(self, **kwargs):
        items = self.validated_data.pop('items')

        ids = []

        for item in items:
            ids.append(item['medicine'])
            if 'medicine' and 'quantity' in item:
                    for idx2,item2 in enumerate(items):
                        if item['medicine'] == item2['medicine'] and item is not item2:
                            item['quantity'] += item2['quantity']
                            items.pop(idx2)

            else:
                raise serializers.ValidationError({"error":"dic must have medicine and quantity"})

        meds = Medicine.objects.filter(id__in=ids,pharmacy_id=self.context['pharmacy_pk'])

        if meds.count() != len(set(ids)):
            raise serializers.ValidationError({"error":"some of the ids are invalid"})

        with transaction.atomic():
            sale = Sale.objects.create(pharmacy_id=self.context['pharmacy_pk'],seller_name=self.context['name'])
            items = SaleItemSerializer(data=items,many=True,context={'sale':sale})
            items.is_valid(raise_exception=True)
            items.save()

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


