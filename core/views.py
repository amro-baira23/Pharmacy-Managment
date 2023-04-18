from django.shortcuts import render
from .models import *
from .serializers import *
from .permissions import *
from rest_framework import views, generics,authentication
# Create your views here.


class MedicineListCreateAPIView(generics.ListCreateAPIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [isMember]
    serializer_class = MedicineSerializer
    
    def get_queryset(self):
        return Medicine.objects.filter(pharmacy=self.kwargs['pk'])
    
    def perform_create(self, serializer):
        return Medicine.objects.create(pharmacy_id=self.kwargs['pk'],brand_name=serializer.data['brand_name'],quantity=serializer.data['quantity'],price=serializer.data['price'],type=serializer.data['type'],barcode=serializer.data['barcode'])
    



    