from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

from rest_framework import serializers
from djoser.serializers import UserCreatePasswordRetypeSerializer as UCPR

from .models import *


User = get_user_model()

roles_map = {
            'S':"saller",
            'P':"purcher",
            'PM':"pharmacy_manager",
            'M':"manager",
            }


# ########## COMPANY ##########

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id','name','phone_number']


    def validate_brand_name(self,name):
        return name.capitalize()

#
## ########## MEDICINE ##########
#
class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = [
            'company',
            'brand_name',
            'barcode',
            'sale_price',
            'purchase_price',
            'need_prescription',
            'min_quanity',
            'type'
        ]


    def validate_brand_name(self,brand_name):
        return brand_name.capitalize()


class MedicineUpdateSerializer(MedicineSerializer):
    class Meta(MedicineSerializer.Meta):
        fields = MedicineSerializer.Meta.fields + ['is_active']
  
    
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
class ShiftListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = ['id','name']


class ShiftSerializer(serializers.ModelSerializer):
    days = serializers.SerializerMethodField("get_days")
    class Meta:
        model = Shift
        fields = ['id','name','start_time','end_time','days']

    def get_days(self,shift):
        return [i.day for i in shift.days.all()]
    

class ShiftAddSerializer(serializers.ModelSerializer):
    days = serializers.ListField(child=serializers.ChoiceField(choices=DAY_CHOICES),write_only=True)
    class Meta:
        model = Shift
        fields = ['id','name','start_time','end_time','days']


    def validate_days(self,days):
        if len(days) != len(set(days)):
            raise serializers.ValidationError("dublicate are not allowed")
        return days


    def validate(self, attrs):
        start = attrs.get('start_time') or self.instance.start_time
        end = attrs.get('end_time') or self.instance.end_time
        if start >= end:
            raise serializers.ValidationError("end time must be after start time")
        return super().validate(attrs)


    def create(self, validated_data):
        days = validated_data.pop('days')

        with transaction.atomic():

            instance = super().create(validated_data)
            shift_days = [ShiftDay(shift=instance,day=i) for i in days]
            ShiftDay.objects.bulk_create(shift_days)

            return instance
        
    def update(self, instance, validated_data):
        days = validated_data.pop('days') if validated_data.get('days') else None
        deleted_days = []
        with transaction.atomic():

            instance = super().update(instance, validated_data)

            if days:
                for d in instance.days.all():
                    if not d.day in days:
                        deleted_days.append(d.day)
                    else:
                        days.remove(d.day)

                instance.days.filter(day__in=deleted_days).delete()

                shifts = [ShiftDay(shift=instance,day=i) for i in days]
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
    roles = serializers.CharField(source="get_roles")
    shift = ShiftListSerializer(read_only=True)
    class Meta:
        model = User
        fields = ['id','first_name', 'last_name', 'email', 'phone_number', 'salry', 'pharmacy','shift','roles']

class EmployeeUpdateSerializer(serializers.ModelSerializer):
    roles = serializers.ChoiceField(choices=ROLE_CHOICES,write_only=True)
    shift = serializers.PrimaryKeyRelatedField(queryset=Shift.objects.all())
    class Meta:
        model = User
        fields = ['first_name','last_name','phone_number','salry','roles','shift']


    def update(self, instance, validated_data):
        with transaction.atomic():
            role = validated_data.get('roles')

            if role:
                validated_data.pop('roles')

                instance.roles.all().delete()

                if role == 'PS':
                    UserRole.objects.bulk_create([UserRole(user=instance,role_id=roles_map[i]) for i in role])            
                else:
                    UserRole.objects.create(user=instance,role_id=roles_map[role])

            instance = super().update(instance, validated_data)

            return instance
    

class EmployeeCreateSerializer(UCPR):
    roles = serializers.ChoiceField(choices=ROLE_CHOICES,write_only=True)
    shift = serializers.PrimaryKeyRelatedField(queryset=Shift.objects.all())
    class Meta:
        model = User
        fields = UCPR.Meta.fields + ("roles","shift",)

    def validate(self, attrs):
        roles = attrs.get("roles")
        del attrs['roles']
        super().validate(attrs)
        attrs['roles'] = roles
        return attrs

    def create(self, validated_data):
        role = validated_data.pop('roles')
        validated_data['pharmacy_id'] = self.context['pharmacy']

        with transaction.atomic():

            user = super().create(validated_data)


            if role == 'PS':
                    UserRole.objects.bulk_create([UserRole(user=user,role_id=roles_map[i]) for i in role])            
            else:
                    UserRole.objects.create(user=user,role_id=roles_map[role])

            return user
        
