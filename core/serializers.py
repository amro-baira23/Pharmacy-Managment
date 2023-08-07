from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from django.db.models import Sum,Subquery,OuterRef,Q
from django.db.models.functions import Coalesce
from rest_framework import serializers
from djoser.serializers import UserCreatePasswordRetypeSerializer as UCPR
from django_q.tasks import async_task

from .models import *
User = get_user_model()

def set_up_items_ids_filter(instance,data,type):
    fil = Q()
    ids = []
    items = []
    
    match type:
        case 1:
            for item in data:
                items.append(DisposedItem(disposal=instance,**item)) 
                ids.append(item['medicine'].id)
                fil |= Q(expiry_date=item["expiry_date"],medicine_id=item["medicine"])

        case 2:
            for item in data:
                items.append(SaleItem(sale=instance,**item)) 
                ids.append(item['medicine'].id)
                fil |= Q(expiry_date=item["expiry_date"],medicine_id=item["medicine"])
        case 3:
            for item in data:
                items.append(ReturnedItem(returment=instance,**item)) 
                ids.append(item['medicine'].id)
                fil |= Q(expiry_date=item["expiry_date"],medicine_id=item["medicine"])
    
    return items,ids,fil


def get_amounts(ids,pharmacy_id,fil):
    purchase = PurchaseItem.objects.filter(purchase__pharmacy_id=pharmacy_id,medicine_id=OuterRef('pk')).filter(fil).values('medicine').annotate(amount_sum=Sum('quantity')).values('amount_sum')
    sale = SaleItem.objects.filter(sale__pharmacy_id=pharmacy_id,medicine_id=OuterRef('pk')).filter(fil).values('medicine').annotate(amount_sum=Sum('quantity')).values('amount_sum')
    dispose = DisposedItem.objects.filter(disposal__pharmacy_id=pharmacy_id,medicine_id=OuterRef('pk')).filter(fil).values('medicine').annotate(amount_sum=Sum('quantity')).values('amount_sum')
    returment = ReturnedItem.objects.filter(returment__pharmacy_id=pharmacy_id,medicine_id=OuterRef('pk')).filter(fil).values('medicine').annotate(amount_sum=Sum('quantity')).values('amount_sum')
    amounts = list(Medicine.objects.filter(id__in=ids).annotate(amount=Coalesce(Subquery(purchase),0)-Coalesce(Subquery(sale),0)-Coalesce(Subquery(dispose),0)+Coalesce(Subquery(returment),0)).values_list('amount','id'))

    return amounts


def purchase_exclude_amounts(instance,items,pharmacy_id,flat=False):

    fil = Q()
    old_dict = {}
    for item in items:
        old_dict[item.medicine.id] = item.expiry_date.strftime("%Y-%m-%d")
        fil |= Q(expiry_date=item.expiry_date,medicine_id=item.medicine.id)
    
    purchase = PurchaseItem.objects.exclude(purchase=instance).filter(purchase__pharmacy_id=pharmacy_id,medicine_id=OuterRef('pk')).filter(fil).values('medicine').annotate(amount_sum=Sum('quantity')).values('amount_sum')
    sale = SaleItem.objects.filter(sale__pharmacy_id=pharmacy_id,medicine_id=OuterRef('pk')).filter(fil).values('medicine').annotate(amount_sum=Sum('quantity')).values('amount_sum')
    dispose = DisposedItem.objects.filter(disposal__pharmacy_id=pharmacy_id,medicine_id=OuterRef('pk')).filter(fil).values('medicine').annotate(amount_sum=Sum('quantity')).values('amount_sum')
    returment = ReturnedItem.objects.filter(returment__pharmacy_id=pharmacy_id,medicine_id=OuterRef('pk')).filter(fil).values('medicine').annotate(amount_sum=Sum('quantity')).values('amount_sum')
    if flat:
        value = 'amount',
    else:
        value = 'amount','id'

    amounts = list(Medicine.objects.filter(id__in=list(old_dict.keys())).order_by().annotate(amount=Coalesce(Subquery(purchase),0)-Coalesce(Subquery(sale),0)-Coalesce(Subquery(dispose),0)+Coalesce(Subquery(returment),0)).values_list(*value,flat=flat))

    return old_dict,amounts


def check_amounts(amounts,items):
    shortage_medicines = []
    for set_item in amounts:
            set_id = set_item[1]
            for item in items:
                if item["medicine"].id == set_id:
                    if set_item[0] - item['quantity'] >= 0:
                       if item['medicine'].min_quanity > set_item[0] - item['quantity']:
                           shortage_medicines.append(item['medicine'].id)
                    else:
                        raise serializers.ValidationError({'error':"There is no purchase for medicine in pharmacy with this date or not enough amount"})
                    break
    
    return shortage_medicines


def preper_items(items):
    seen_items = {}

    for item in items:
        if set(item.keys()) != {'medicine', 'quantity', 'price', 'expiry_date'}:
            raise serializers.ValidationError(_('item should have have medicine quantity and price only'))
        if 0 >= item['quantity']:
            raise serializers.ValidationError('quantity should be gretter than 0')
        if 0 >= item['price']:
            raise serializers.ValidationError('price should be gretter than 0')
        
        key = (item['medicine'])

        if key in seen_items:
            existing_item = seen_items[key]
            
            if existing_item['price'] != item['price'] or existing_item['expiry_date'] != item['expiry_date']:
                raise serializers.ValidationError(_('same item with diffrent price exist or expiry_date exist'))
            existing_item['quantity'] += item['quantity']

        else:
            seen_items[key] = item

    items.clear()
    items.extend(seen_items.values())
    return items


def create_items(serializer,items,context):
    item_serializer = serializer(data=items,many=True,context=context)
    if not item_serializer.is_valid():
        raise serializers.ValidationError({'error':_('some items are invalid')})
    item_serializer.save()


def update_items(instance,serializer,items,context):
    if items:
        item_serializer = serializer(data=items,many=True,context=context)
        with transaction.atomic():
            instance.items.all().delete()
            if not item_serializer.is_valid():
                raise serializers.ValidationError({'error':_('some items are invalid')})
            item_serializer.save()


## ########## RETRIVEDITEM ##########


class RetrivedItemListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        returment = self.context['returment']
        pharmacy_id = self.context['pharmacy_pk']

        items,ids,fil = set_up_items_ids_filter(returment,validated_data,3)

        sale = SaleItem.objects.filter(sale__pharmacy_id=pharmacy_id,medicine_id=OuterRef('pk')).filter(fil).values('medicine').annotate(amount_sum=Sum('quantity')).values('amount_sum')
        returment = ReturnedItem.objects.filter(returment__pharmacy_id=pharmacy_id,medicine_id=OuterRef('pk')).filter(fil).values('medicine').annotate(amount_sum=Sum('quantity')).values('amount_sum')
        amounts = list(Medicine.objects.filter(id__in=ids).annotate(amount=Coalesce(Subquery(sale),0)-Coalesce(Subquery(returment),0)).values_list('amount','id'))

        for set_item in amounts:
            set_id = set_item[1]
            for item in validated_data:
                if item["medicine"].id == set_id:
                    if  0 > set_item[0] - item['quantity']:
                        raise serializers.ValidationError({'error':"There is no purchase for medicine in pharmacy with this date or not amount"})
                    break

        return ReturnedItem.objects.bulk_create(items)
    

class RetrivedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnedItem
        fields = ['id','medicine','quantity','price','expiry_date']
        list_serializer_class = RetrivedItemListSerializer


## ########## RETRIVE ##########


class RetriveListSerializer(serializers.ModelSerializer):
   user = serializers.StringRelatedField()
   value = serializers.IntegerField()
   class Meta:
       model = Returment
       fields = ['id','user','time','value']


class RetriveSerializer(serializers.ModelSerializer):
    items = RetrivedItemSerializer(many=True)
    user = serializers.StringRelatedField()
    class Meta:
           model = Returment
           fields = ['id','user','items','time']


class RetriveAddSerializer(serializers.ModelSerializer):
    items = serializers.ListField(child=serializers.DictField(),write_only=True,min_length=1)
    class Meta:
       model = Returment
       fields = ['items']

    def validate_items(self,items):     
       return preper_items(items)
    
    def create(self, validated_data):
        items = validated_data.pop('items')
        pharmacy_id = self.context['pharmacy_pk']
        user_id = self.context['user']

        with transaction.atomic():
            self.instance = Returment.objects.create(pharmacy_id=pharmacy_id,user_id=user_id)
            new_context = {'returment':self.instance,'pharmacy_pk':pharmacy_id}
            
            create_items(RetrivedItemSerializer,items,new_context)

        return self.instance

    def update(self, instance, validated_data):
        items = validated_data.get('items')

        new_context = {'returment':instance,'pharmacy_pk':self.context['pharmacy_pk']}

        update_items(instance,RetrivedItemSerializer,items,new_context)
         
        return instance
   

## ########## DISPOSEDITEM ##########


class DisposedItemListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        disposal = self.context['disposal']
        pharmacy_id = self.context['pharmacy_pk']

        items,ids,fil = set_up_items_ids_filter(disposal,validated_data,1)

        amounts = get_amounts(ids,pharmacy_id,fil)

        notifaid_medicines = check_amounts(amounts,validated_data)

        created_items = DisposedItem.objects.bulk_create(items)

        if notifaid_medicines:
            async_task('core.tasks.send_notifications',pharmacy_id,notifaid_medicines) 

        return created_items

class DisposedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisposedItem
        fields = ['id','medicine','quantity','price','expiry_date']
        list_serializer_class = DisposedItemListSerializer


## ########## DISPOSE ##########


class DisposalListSerializer(serializers.ModelSerializer):
   user = serializers.StringRelatedField()
   value = serializers.IntegerField()
   class Meta:
       model = Disposal
       fields = ['id','user','time','value']


class DisposalSerializer(serializers.ModelSerializer):
    items = DisposedItemSerializer(many=True)
    user = serializers.StringRelatedField()
    class Meta:
           model = Disposal
           fields = ['id','user','items','time']


class DisposalAddSerializer(serializers.ModelSerializer):
    items = serializers.ListField(child=serializers.DictField(),write_only=True,min_length=1)
    class Meta:
       model = Disposal
       fields = ['items']

    def validate_items(self,items):     
       return preper_items(items)
    
    def create(self, validated_data):
        items = validated_data.pop('items')
        pharmacy_id = self.context['pharmacy_pk']
        user_id = self.context['user']

        with transaction.atomic():
            self.instance = Disposal.objects.create(pharmacy_id=pharmacy_id,user_id=user_id)
            new_context = {'disposal':self.instance,'pharmacy_pk':pharmacy_id}
            
            create_items(DisposedItemSerializer,items,new_context)

        return self.instance

    def update(self, instance, validated_data):
        items = validated_data.get('items')

        new_context = {'disposal':instance,'pharmacy_pk':self.context['pharmacy_pk']}

        update_items(instance,DisposedItemSerializer,items,new_context)
         
        return instance
   
    
## ########## SALEITEM ##########
   

class SaleItemListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        sale = self.context['sale']
        pharmacy_id = self.context['pharmacy_pk']

        items,ids,fil = set_up_items_ids_filter(sale,validated_data,2)

        amounts = get_amounts(ids,pharmacy_id,fil)

        notifaid_medicines = check_amounts(amounts,validated_data)

        created_items = SaleItem.objects.bulk_create(items)

        if notifaid_medicines:
            async_task('core.tasks.send_notifications',pharmacy_id,notifaid_medicines) 

        return created_items


class SaleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleItem
        fields = ['id','medicine','quantity','price','expiry_date']
        list_serializer_class = SaleItemListSerializer

## ########## SALE ##########

class SaleListSerializer(serializers.ModelSerializer):
   seller = serializers.StringRelatedField()
   value = serializers.IntegerField()
   class Meta:
       model = Sale
       fields = ['id','seller','time',"value"]

class SaleSerializer(serializers.ModelSerializer):
   items = SaleItemSerializer(many=True)
   seller = serializers.StringRelatedField()
   class Meta:
       model = Sale
       fields = ['id','seller','doctor_name','coustomer_name','items','time']


class SaleAddSerializer(serializers.ModelSerializer):
    items = serializers.ListField(child=serializers.DictField(),write_only=True,min_length=1)
    class Meta:
       model = Sale
       fields = ['doctor_name','coustomer_name','items']

    def validate_items(self,items):     
        return preper_items(items)
    
    def create(self, validated_data):
        items = validated_data.pop('items')
        pharmacy_id=self.context['pharmacy_pk']
        seller_id=self.context['seller']

        with transaction.atomic():
            self.instance = Sale.objects.create(pharmacy_id=pharmacy_id,seller_id=seller_id,**validated_data)
            new_context = {'sale':self.instance,'pharmacy_pk':pharmacy_id}
            
            create_items(SaleItemSerializer,items,new_context)

        return self.instance

    def update(self, instance, validated_data):
        instance.doctor_name = validated_data.get('doctor_name',instance.doctor_name)
        instance.coustomer_name = validated_data.get('coustomer_name',instance.coustomer_name)
        items = validated_data.get('items')

        new_context = {'sale':instance,'pharmacy_pk':self.context['pharmacy_pk']}

        update_items(instance,SaleItemSerializer,items,new_context)
         
        return instance
    
   
## ########## PURCHASEITEM ##########


class PurchaseItemListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        items = [PurchaseItem(purchase=self.context['purchase'],**item) for item in validated_data]
        return PurchaseItem.objects.bulk_create(items)


class PurchaseItemSerializer(serializers.ModelSerializer):
    class Meta:
       model = PurchaseItem
       fields = ['id','medicine','quantity','price','expiry_date']
       list_serializer_class = PurchaseItemListSerializer
   

# ########## PURCHASE ##########


class PurchaseListSerializer(serializers.ModelSerializer):
   reciver = serializers.CharField(read_only=True)
   value = serializers.IntegerField()
   class Meta:
       model = Purchase
       fields = ['id','reciver','time','value']
   

class PurchaseSerializer(serializers.ModelSerializer):
   items = PurchaseItemSerializer(many=True)
   reciver = serializers.StringRelatedField()
   class Meta:
       model = Purchase
       fields = ['id','reciver','time','items']
 

class PurchaseAddSerializer(serializers.ModelSerializer):
    items = serializers.ListField(child=serializers.DictField(),write_only=True,min_length=1)
    class Meta:
        model = Purchase
        fields = ['items']

    def validate_items(self,items):     
        return preper_items(items)

    def create(self, validated_data):
        reciver_id=self.context['reciver']
        pharmacy_id=self.context['pharmacy_pk']
        items = validated_data.pop('items')

        with transaction.atomic():
            self.instance = Purchase.objects.create(reciver_id=reciver_id,pharmacy_id=pharmacy_id)
            new_context = {'purchase':self.instance}

            create_items(PurchaseItemSerializer,items,new_context)

        return self.instance
   
    def update(self, instance, validated_data):
        items = validated_data.get('items')
        old_items = instance.items.select_related('medicine').all()
        pharmacy_id = self.context['pharmacy_pk']
        new_context = {'purchase':self.instance}
        if items:
            
            old_dict , amounts = purchase_exclude_amounts(instance,old_items,pharmacy_id)
        
            for set_item in amounts:
                med_id = set_item[1]
                for item in items:
                    if item["medicine"] == med_id and item['expiry_date'] == old_dict[med_id]:
                        res = set_item[0] + item['quantity']
                        if 0 > res:
                            raise serializers.ValidationError({'error':'cant make this change some total amount will become negative'})
                        break

            update_items(instance,PurchaseItemSerializer,items,new_context)

        return instance
   

## ########## SHIFT ##########


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
    days = serializers.ListField(child=serializers.ChoiceField(choices=DAY_CHOICES),write_only=True,min_length=1)
    class Meta:
        model = Shift
        fields = ['id','name','start_time','end_time','days']


    def validate_days(self,days):
        if len(days) != len(set(days)):
            raise serializers.ValidationError("dublicate are not allowed")
        return days

    def validate_name(self,name):
        return name.capitalize()

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
        days = validated_data.get('days')
        with transaction.atomic():
            if days:
                validated_data.pop('days')
                instance.days.all().delete()
                shifts = [ShiftDay(shift=instance,day=i) for i in days]
                ShiftDay.objects.bulk_create(shifts)
            instance = super().update(instance, validated_data)
            return instance

## ########## USERROLE ##########


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ['id','role']


## ########## PHARMACY ##########


class PharmacyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        fields = ['id','name']


class PharmacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        fields = ['id','name','city','street','region','phone_number']

    
## ########## EMPLOYEE ##########


class EmployeeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','name']


class EmployeeSerializer(serializers.ModelSerializer):
    roles = serializers.CharField(source="get_roles")
    shift = ShiftListSerializer(read_only=True)
    class Meta:
        model = User
        fields = ['id','first_name','last_name','email','phone_number','salry','pharmacy','shift','roles']


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    roles = serializers.ChoiceField(choices=ROLE_CHOICES,write_only=True)
    shift = serializers.PrimaryKeyRelatedField(queryset=Shift.objects.all())
    
    class Meta:
        model = User
        fields = ['first_name','last_name','phone_number','salry','roles','shift','is_active']

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

    def validate_roles(self,role):
        if role == 'M' and not self.context['is_manager']:
            raise serializers.ValidationError('only manager can add another manager')
        return role

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
        
class UnactEmployeeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['is_active']


 ########### COMPANY ##########

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id','name','phone_number']


    def validate_name(self,name):
        return name.capitalize()


## ########## MEDICINE ##########


class MedicineListSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField()
    class Meta:
        model = Medicine
        fields = [
            'id',
            'brand_name',
            'company',
            'quantity'
        ]



class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = [
            'id',
            'company',
            'brand_name',
            'barcode',
            'sale_price',
            'purchase_price',
            'need_prescription',
            'min_quanity',
            'type',
        ]

    def validate_brand_name(self,brand_name):
        return brand_name.capitalize()


class MedicineUpdateSerializer(MedicineSerializer):
    class Meta(MedicineSerializer.Meta):
        fields = MedicineSerializer.Meta.fields + ['is_active']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['title','body','type','time_stamp']