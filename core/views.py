from django.utils.translation import gettext as _
from django.db.models import Sum,Subquery,OuterRef
from django.db.models.functions import Coalesce

from rest_framework import viewsets,response,status

from .models import *
from .serializers import *
from .permissions import *

class PharmacyViewSet(viewsets.ModelViewSet):
    serializer_class = PharmacySerializer

    def get_queryset(self):
        user = self.request.user
        if 'manager' in user.roles.values_list('role',flat=True):
            return Pharmacy.objects.all()
        return Pharmacy.objects.filter(id=user.pharmacy_id)

    
    def get_permissions(self):
        if self.action == 'retrieve':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(),GenralManagerPermission()]

    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if Purchase.objects.filter(pharmacy=instance).exists():
            return response.Response({'detail':'cant delete when there are purchase'})

        
        if Sale.objects.filter(pharmacy=instance).exists():
            return response.Response({'detail':'cant delete when there are sales'})

        with transaction.atomic():
            instance.employees.all().delete()
            instance.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)


class PharmacyEmployeeViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated,ManagerOrPharmacyManagerPermission]

    def get_queryset(self):
        queryset = User.objects.filter(pharmacy_id=self.kwargs['pharmacy_pk'],is_active=True)
        if self.action == 'retrieve':
            queryset = queryset.select_related('shift')
        return queryset
                   
    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer
        elif self.action == 'create' :
            return EmployeeCreateSerializer
        elif self.action in ['update','partial_update'] :
            return EmployeeUpdateSerializer
        return EmployeeSerializer
    
    def get_serializer_context(self):
        return {'pharmacy':self.kwargs['pharmacy_pk']}

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
    

class ShiftViewSet(viewsets.ModelViewSet):
    queryset = Shift.objects.all()
    permission_classes = [permissions.IsAuthenticated,ManagerPermission]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ShiftListSerializer
        elif self.action == 'retrieve':
            return ShiftSerializer
        return ShiftAddSerializer
    
    def destroy(self, request, *args, **kwargs):
        if User.objects.filter(shift=self.get_object()).count() > 0:
            return response.Response({"error":"you must change all users shift to another one before deleting it"},status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)
        

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated,ManagerPermission]

    def destroy(self, request, *args, **kwargs):
        company = self.get_object()
        if Medicine.objects.filter(company=company).count() > 0:
            return response.Response({"error":"you must change all Medicines company to another one before deleting it"},status.HTTP_403_FORBIDDEN)
        company.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class MedicineViewset(viewsets.ModelViewSet):

    
    def get_queryset(self):
        sales = SaleItem.objects.filter(medicine=OuterRef('pk'),sale__pharmacy_id=1).values('medicine').annotate(amount_sum=Sum('quantity')).values('amount_sum')
        purchase = PurchaseItem.objects.filter(medicine=OuterRef('pk'),purchase__pharmacy_id=1).values('medicine').annotate(amount_sum=Sum('quantity')).values('amount_sum')
        return Medicine.objects.annotate(amount=Coalesce(Subquery(purchase),0) - Coalesce(Subquery(sales),0))
        
    
    def get_serializer_class(self):
        if self.request.method in ['PUT','PATCH']:
            return MedicineUpdateSerializer
        return MedicineSerializer
        
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [ManagerPermission()]
         
    def destroy(self, request, *args, **kwargs):
        medicine = self.get_object()
        if SaleItem.objects.filter(medicine=medicine).exists():
            return response.Response({'error':_('cant delete a medicine which sold once but you can archive it')})
        medicine.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class PurchaseViewset(viewsets.ModelViewSet):

   def get_queryset(self):
       return Purchase.objects.prefetch_related('items').filter(pharmacy_id=self.kwargs['pharmacy_pk'])
   
   def get_serializer_class(self):
        if self.action == 'list':
            return PurchaseListSerializer
        elif self.action == 'retrieve':
            return PurchaseSerializer
        return PurchaseAddSerializer

   def get_serializer_context(self):
       user = self.request.user
       reciver = user.id
       return {'pharmacy_pk':self.kwargs['pharmacy_pk'],'reciver':reciver}
   
   def get_permissions(self):
       if self.action == 'delete':
           return [permissions.IsAuthenticated(),ManagerOrPharmacyManagerPermission()]
       return [permissions.IsAuthenticated()]
   
 

class SaleViewset(viewsets.ModelViewSet):

    def get_queryset(self):
            queryset = Sale.objects.prefetch_related('seller').filter(pharmacy_id=self.kwargs['pharmacy_pk'])
            if self.action == 'retrieve':
                queryset = queryset.prefetch_related('items')
            return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SaleListSerializer
        elif self.action == 'retrieve':
            return SaleSerializer
        return SaleAddSerializer
    
    def get_serializer_context(self):
        user = self.request.user
        seller = user.id
        return {'pharmacy_pk':self.kwargs['pharmacy_pk'],'seller': seller}
    
    def get_permissions(self):
        if self.action == 'delete':
            return [permissions.IsAuthenticated(),ManagerOrPharmacyManagerPermission()]
        return [permissions.IsAuthenticated()]
    