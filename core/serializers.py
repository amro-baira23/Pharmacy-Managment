from .models import *
from rest_framework import serializers


class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = [
            'brand_name',
            'barcode',
            'type',
            'quantity',
            'price',
        ]

class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = [
            ''
        ]