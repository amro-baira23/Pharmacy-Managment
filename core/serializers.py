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