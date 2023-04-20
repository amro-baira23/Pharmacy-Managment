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
            'pharmacy',
            'reciver_name',
            'items'
        ]
        read_only_fields = ['pharmacy']
    
    def get_items(self,obj):
        items = PurchaseItem.objects.filter(purchase_id=obj.id)
        items = PurchaseItemSerializer(items,many=True).data
        return items

    def save(self, **kwargs):
        print('hi save!')
        # print("kwargs:",kwargs['it'])
        return super().save(**kwargs)

class PurchaseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseItem
        fields = [
            'medicine',
            'quantity',
            'price',
        ]

 
    def create(self, validated_data):
        quantity = validated_data['quantity']
        medicine = validated_data['medicine']
        medicine.quantity -= quantity
        medicine.save()
        return super().create(validated_data)