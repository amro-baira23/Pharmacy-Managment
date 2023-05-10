from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

from rest_framework import serializers
from djoser.serializers import UserCreatePasswordRetypeSerializer as UCPR

from .models import *


User = get_user_model()

# ########## COMPANY ##########

#class CompanySerializer(serializers.ModelSerializer):
#    class Meta:
#        model = Company
#        fields = ['id','name']
#
## ########## MEDICINE ##########
#
#class MedicineListSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = Medicine
#        fields = [
#            'id',
#            'quantity',
#            'price',
#            'need_prescription',
#            'is_expired',
#            'brand_name',
#            'barcode',
#            'company',
#            'type',
#        ]
#  
#
#class MedicineCreateSerializer(serializers.ModelSerializer):
#    company_name = serializers.CharField(max_length=50,write_only=True,required=False,allow_blank=True)
#    class Meta:
#        model = Medicine
#        fields = [
#            'id',
#            'company_name',
#            'brand_name',
#            'barcode',
#            'price',
#            'need_prescription',
#            'type',
#            'substances'
#        ]
#
#    
#    def validate_brand_name(self,name):
#        return name.capitalize()
#  
#    def create(self, validated_data):
#        name = validated_data.get('company_name')
#        substances = validated_data.get('substances')
#        ph_id = self.context['pharmacy_pk']
#        company = None
#
#        with transaction.atomic():
#            if name:
#                name = name.capitalize()
#                validated_data.pop('company_name')
#                company, created = Company.objects.get_or_create(pharmacy_id=ph_id,name=name)
#            
#            medicine , created = Medicine.unique_medicine.get_or_create(ph_id,company,validated_data)
#
#            if not created:
#                raise serializers.ValidationError({'error':_('medicine with this data already exist')})
#            
#            if substances:
#                validated_data.pop("substances")
#                valid_subs = list(Substance.objects.filter(pharmacy_id=ph_id,name__in=substances))
#            
#                for sub in valid_subs:
#                     if sub.name in substances:
#                         substances.remove(sub.name)
#            
#                created_substances = [Substance.objects.create(name=name,pharmacy_id=ph_id) for name in substances]
#
#                all_sub = created_substances + valid_subs
#
#                final_subs = [MedicineSubstance(medicine=medicine,substance=sub) for sub in all_sub]
#                MedicineSubstance.objects.bulk_create(final_subs)
#
#            return medicine
#        
#
#class MedicineUpdateSerializer(serializers.ModelSerializer):
#    company_name = serializers.CharField(max_length=50,write_only=True,required=False,allow_blank=True)
#    class Meta:
#        model = Medicine
#        fields = [
#            'brand_name',
#            'barcode',
#            'company_name',
#            'type',
#            'quantity',
#            'price',
#            'expiry_date',
#            'need_prescription',
#            'is_active'
#        ]
#
#    def validate_brand_name(self,name):
#        return name.capitalize()
#    
#    def validate_company_name(self,company_name):
#        return company_name.capitalize()
#
#    def update(self, instance, validated_data):
#
#        ph_id = self.context['pharmacy_pk']
#        com_name = validated_data.get('company_name')
#        company = instance.company if instance.company is not None and self.partial else None
#        
#
#        validated_data['barcode'] = validated_data.get('barcode') or instance.barcode
#        validated_data['brand_name'] = validated_data.get('brand_name') or instance.brand_name
#        validated_data['type'] = validated_data.get('type') or instance.type
#
#
#        with transaction.atomic():
#
#            if com_name is not None and com_name != '':
#                company, created = Company.objects.get_or_create(pharmacy_id=ph_id,name=com_name)
#
#            try:
#                medicine = Medicine.unique_medicine.get(ph_id,validated_data)
#                if medicine != instance:
#                    raise serializers.ValidationError({'error':_('cant update medicine , with same data already exist')})
#            except Medicine.DoesNotExist:
#                pass
#            
#            instance.company = company
#            instance = super().update(instance, validated_data)
#            return instance
#
## ########## SALEITEM ##########
#    
#class SaleItemSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = SaleItem
#        fields = [
#            'id',
#            'medicine',
#            'quantity',
#            'price',
#        ]
#
#    def validate(self, attrs):
#        medicine = attrs.get('medicine')
#        if medicine.pharmacy.id != int(self.context['pharmacy_pk']):
#            raise serializers.ValidationError(_('no medicine with such id for this pharmacy'))
#        return super().validate(attrs)
#
#    
#    def create(self, validated_data):
#        medicine = validated_data['medicine']
#        quantity = validated_data['quantity']
#        with transaction.atomic():
#            medicine.quantity -= quantity
#            if medicine.quantity < 0:
#                raise serializers.ValidationError({'error':_('not enough medicine %(name)s in enventory') % {'name':medicine.brand_name}})
#            medicine.save()
#            return SaleItem.objects.create(sale=self.context['sale'],**validated_data)
#
## ########## SALE ##########
#
#class SaleListSerializer(serializers.ModelSerializer):
#    seller_name = serializers.CharField(read_only=True)
#    class Meta:
#        model = Sale
#        fields = [
#            'id',
#            'seller_name',
#            'time',
#        ]
#
#
#class SaleSerizlizer(serializers.ModelSerializer):
#    items = SaleItemSerializer(many=True)
#    class Meta:
#        model = Sale
#        fields = ['id','seller_name','items','time']
#
#
#class SaleCreateSerializer(serializers.ModelSerializer):
#    items = serializers.ListField(child=serializers.JSONField(),write_only=True)
#    class Meta:
#        model = Sale
#        fields = ['items']
#
#
#    def validate_items(self,items):
#        if len(items) == 0:
#            raise serializers.ValidationError(_('sale should have atleast one item'))
#        
#        for item in items:
#            if type(item) is not dict:
#                raise serializers.ValidationError(_('sale item should be dict'))
#            
#            if list(item.keys()) != ['medicine','quantity','price']:
#                raise serializers.ValidationError(_('sale item should have have medicine quantity and price only'))
#
#        for item in items:
#            for idx2,item2 in enumerate(items):
#                if item['medicine'] == item2['medicine'] and item is not item2:
#                    if item['price'] != item2['price']:
#                        raise serializers.ValidationError(_('same item in the sale with diffrent price exist'))
#                    item['quantity'] += item2['quantity']
#                    items.pop(idx2)
#  
#        return items
#
#    def save(self, **kwargs):
#        self.instance = Sale.objects.create(pharmacy_id=self.context['pharmacy_pk'],seller_name=self.context['name'])
#        return self.instance
#
## ########## PURCHASEITEM ##########
#
#class PurchaseItemSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = PurchaseItem
#        fields = ['id','medicine','quantity','price']
#
#    def validate(self, attrs):
#        medicine = attrs.get('medicine')
#        if medicine.pharmacy.id != int(self.context['pharmacy_pk']):
#            raise serializers.ValidationError(_('no medicine with such id for this pharmacy'))
#        return super().validate(attrs)
#    
#    def create(self, validated_data):
#        medicine = validated_data['medicine']
#        quantity = validated_data['quantity']
#        with transaction.atomic():
#            medicine.quantity += quantity
#            medicine.save()
#            return PurchaseItem.objects.create(purchase=self.context['purchase'],**validated_data)
#
## ########## PURCHASE ##########
#
#class PurchaseListSerializer(serializers.ModelSerializer):
#    class Meta:
#        model = Purchase
#        fields = [
#            'id',
#            'reciver_name',
#            'time'
#        ]
#    
#
#class PurchaseSerializer(serializers.ModelSerializer):
#    items = PurchaseItemSerializer(many=True)
#    class Meta:
#        model = Purchase
#        fields = [
#            'id',
#            'reciver_name',
#            'time',
#            'items'
#        ]
#    
#
#class PurchaseCreateSerializer(serializers.ModelSerializer):
#    items = PurchaseItemSerializer(many=True)
#    class Meta:
#        model = Purchase
#        fields = ['items']
#
#    def validate_items(self,items):
#        if len(items) == 0:
#            raise serializers.ValidationError(_('sale should have atleast one item'))
#        return items
#
#    def save(self, **kwargs):
#        self.instance = Purchase.objects.create(reciver_name=self.context['name'],pharmacy_id=self.context['pharmacy_pk'])
#        return self.instance
#    
## ########## PHARMACY ##########
#

class PharmacyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        fields = ['id','name']


class PharmacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        fields = ['name','city','street','phone_number']

    
## ########## EMPLOYEE ##########
#
class EmployeeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','name']


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','first_name', 'last_name', 'email', 'phone_number', 'salry', 'role', 'pharmacy']


class EmployeeCreateSerializer(UCPR):
    role = serializers.ChoiceField(ROLE_CHOICES)
    class Meta:
        model = User
        fields = UCPR.Meta.fields + ('role',)

    def create(self, validated_data):
        validated_data['pharmacy_id'] = self.context['pharmacy']
        return super().create(validated_data)