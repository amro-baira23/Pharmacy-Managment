from django.shortcuts import render
from .models import *
from .serializers import *
from .permissions import *
from rest_framework import views, generics,authentication,permissions
# Create your views here.


class MedicineListCreateAPIView(generics.ListCreateAPIView):
    queryset = Medicine.objects.all()
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [isMember]
    serializer_class = MedicineSerializer
    # authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated, isMember]
    
    def get_queryset(self):
        return Medicine.objects.all().filter(pharmacy=self.kwargs['pk'])
    
    def perform_create(self, serializer):
        medicine = Medicine.objects.create(pharmacy_id=self.kwargs['pk'],brand_name=serializer.data['brand_name'],
            quantity=serializer.data['quantity'],company_id=serializer.data['company'],price=serializer.data['price'],
            type=serializer.data['type'],barcode=serializer.data['barcode'])
        
        return medicine
    

class PurchaseListCreateAPIView(generics.ListCreateAPIView):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = [permissions.IsAuthenticated, isMember]

    def get_queryset(self):
        qs = Purchase.objects.all().filter(pharmacy=self.kwargs['pk'])
        if qs.exists():
            return qs
        else:
            raise Exception("Such list doesn't exist")
    
    def perform_create(self, serializer):
        items = self.request.data.get('item')
        if not items:
            raise Exception("Purchase order can't be empty")
        print('after exp')
        purchase = Purchase.objects.create(pharmacy_id=self.kwargs['pk'], reciver_name=serializer.data['reciver_name'])
        print('body: ',items)
        for item in items:
            PurchaseItem.objects.create(purchase_id=purchase.id,medicine_id=item['medicine'],quantity=item['quantity'],price=item['price'])
            medicine = Medicine.objects.get(id=item['medicine'])
            medicine.quantity -= item['quantity']
            medicine.save()
        return serializer
  