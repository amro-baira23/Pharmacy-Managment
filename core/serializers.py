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
#            'brand_name',
#            'barcode',
#            'sale_price',
#            'purchase_price',
#            'type',
#            'need_prescription',
#            'company',
#        ]
#  
#
#class MedicineCreateSerializer(serializers.ModelSerializer):
#    company = serializers.CharField(write_only=True,max_length=50)
#    class Meta:
#        model = Medicine
#        fields = [
#            'id',
#            'company',
#            'brand_name',
#            'barcode',
#            'sale_price',
#            'purchase_price',
#            'need_prescription',
#            'type',
#        ]
#  
#    def create(self, validated_data):
#        with transaction.atomic():
#            
#            company , created = Company.objects.get_or_create(name=validated_data.pop('company'))
#            validated_data['company'] = company
#
#            medicine , created = Medicine.unique_medicine.get_or_create(validated_data)
#            if not created:
#                raise serializers.ValidationError({'error':_('medicine with this data already exist')})
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
#            'sale_price',
#            'purchase_price',
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

## ########## ROLES ##########

class ShiftSerializer(serializers.ModelSerializer):
    days = serializers.SerializerMethodField("get_days")
    class Meta:
        model = Shift
        fields = ['id','name','start_time','end_time','days']

    def get_days(self,shift):
        return [i.day.id for i in shift.days.all()]
    

class ShiftAddSerializer(serializers.ModelSerializer):
    days = serializers.ListField(child=serializers.IntegerField(min_value=1,max_value=7),min_length=1,max_length=7,write_only=True)
    class Meta:
        model = Shift
        fields = ['id','name','start_time','end_time','days']


    def validate_days(self,days):
        if len(days) != len(set(days)):
            raise serializers.ValidationError("dublicate are not allowed")
        return days


    def validate(self, attrs):
        start = attrs.get('start_time')
        end = attrs.get('end_time')
        if start >= end:
            raise serializers.ValidationError("end time must be after start time")
        return super().validate(attrs)


    def create(self, validated_data):
        days = validated_data.pop('days')

        with transaction.atomic():

            instance = super().create(validated_data)
            shift_days = [ShiftDay(shift=instance,day_id=id) for id in days]
            ShiftDay.objects.bulk_create(shift_days)

            return instance
        
    def update(self, instance, validated_data):
        days = validated_data.pop('days') if validated_data.get('days') else None
        deleted_days = []
        with transaction.atomic():

            instance = super().update(instance, validated_data)

            for day in instance.days.all():
                if not day.day.id in days:
                    deleted_days.append(day.day.id)
                else:
                    days.remove(day.day.id)

            instance.days.filter(day_id__in=deleted_days).delete()

            shifts = [ShiftDay(shift=instance,day_id=id) for id in days]
            ShiftDay.objects.bulk_create(shifts)

            return instance

class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ['id','role']


## ########## PHARMACY ##########
#

class PharmacyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        fields = ['id','name']


class PharmacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        fields = ['id','name','city','street','region','phone_number']

    
## ########## EMPLOYEE ##########
#
class EmployeeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','name']


class EmployeeSerializer(serializers.ModelSerializer):
    roles = UserRoleSerializer(many=True,read_only=True)
    shift = ShiftSerializer(read_only=True)
    class Meta:
        model = User
        fields = ['id','first_name', 'last_name', 'email', 'phone_number', 'salry', 'pharmacy','shift','roles']

class EmployeeUpdateSerializer(serializers.ModelSerializer):
    roles = serializers.ListField(child=serializers.BooleanField(),min_length=4,max_length=4,write_only=True)
    class Meta:
        model = User
        fields = ['first_name','last_name','phone_number','salry','roles','shift']

    def validate_roles(self,roles):
        for i in roles:
            if i:
                return roles
        raise serializers.ValidationError("atleast one value shoud be true")

    def update(self, instance, validated_data):
        with transaction.atomic():
            roles = validated_data.get('roles')

            if roles:
                validated_data.pop('roles')

                pre_roles = ['saller','purcher','pharmacy_manager','manager']
                in_roles = []
                out_roles = []
    
                user_roles = instance.roles.all()
                names = user_roles.values_list('role',flat=True)
    
                for idx,i in enumerate(roles):
                    if i :
                        if pre_roles[idx] not in names: 
                            in_roles.append((UserRole(role_id=pre_roles[idx],user=instance)))
                    else:
                        out_roles.append(pre_roles[idx])
        
                instance.roles.filter(role__in=out_roles).delete()
    
                UserRole.objects.bulk_create(in_roles)

            instance = super().update(instance, validated_data)

            return instance
    

class EmployeeCreateSerializer(UCPR):
    roles = serializers.ListField(child=serializers.BooleanField(),min_length=4,max_length=4,write_only=True)
    class Meta:
        model = User
        fields = UCPR.Meta.fields + ("roles","shift",)

    def validate_roles(self,roles):
        for i in roles:
            if i:
                return roles
        raise serializers.ValidationError("atleast one value shoud be true")

    def validate(self, attrs):
        print(attrs)
        roles = attrs.get("roles")
        del attrs['roles']
        super().validate(attrs)
        attrs['roles'] = roles
        return attrs

    def create(self, validated_data):
        roles = validated_data.pop('roles')
        validated_data['pharmacy_id'] = self.context['pharmacy']

        user = super().create(validated_data)

        pre_roles = ['saller','purcher','pharmacy_manager','manager']
        user_perms = []

        for idx,i in enumerate(roles):
            if i:
               user_perms.append(UserRole(role_id=pre_roles[idx],user=user)) 

        UserRole.objects.bulk_create(user_perms)

        return user
    
