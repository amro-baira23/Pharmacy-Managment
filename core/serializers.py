from .models import *
from rest_framework import serializers


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
        fields = ['user','role']
