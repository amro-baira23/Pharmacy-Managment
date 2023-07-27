from django.utils.translation import gettext as _
from django.db.models import Sum,Subquery,OuterRef
from django.db.models.functions import Coalesce
from rest_framework.decorators import action

from rest_framework import viewsets,response,status,mixins
from rest_framework.views import APIView

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
        is_manager = self.request.user.roles.filter(role__name="manager").exists()
        return {'pharmacy':self.kwargs['pharmacy_pk'],"is_manager":is_manager}

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
    
class UnactiveEmployeeViewSet(viewsets.ModelViewSet):
    http_method_names = ['get','patch','options']

    def partial_update(self, request, *args, **kwargs):
        request.data.update({"is_active":True})
        print(request.data)
        return super().partial_update(request, *args, **kwargs)

    def get_queryset(self):
        queryset = User.objects.filter(pharmacy_id=self.kwargs['pharmacy_pk'],is_active=False)
        return queryset
        
    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer
        elif self.action == 'partial_update':
            return UnactEmployeeUpdateSerializer
        return EmployeeSerializer
      
    def get_serializer_context(self):
        user = self.request.user.id
        return {'pharmacy_pk':self.kwargs['pharmacy_pk'],'user': user}
     

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
        queryset = Purchase.objects.prefetch_related('reciver').filter(pharmacy_id=self.kwargs['pharmacy_pk'])
        if self.action == 'retrieve':
            queryset = queryset.prefetch_related('items')
        return queryset
   
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
       return [permissions.IsAuthenticated(),PurchasePermission()]
   
    def destroy(self, request, *args, **kwargs):
        purchase = self.get_object()
        items = purchase.items.select_related('medicine').all()
        pharmacy_id = self.kwargs['pharmacy_pk']

        with transaction.atomic():

            old_dict ,amounts = purchase_exclude_amounts(purchase,items,pharmacy_id,True)

            for item in amounts:
                if 0 > item:
                    raise serializers.ValidationError({'error':'cant make this change some total amount will become negative'})
           
            items.delete()

        return super().destroy(request, *args, **kwargs)
      

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
        return [permissions.IsAuthenticated(),SalerPermission()]
    
    def destroy(self, request, *args, **kwargs):
        sale = self.get_object()
        with transaction.atomic():
            sale.items.all().delete()
            return super().destroy(request, *args, **kwargs)


class DisposalViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
            queryset = Disposal.objects.prefetch_related('user').filter(pharmacy_id=self.kwargs['pharmacy_pk'])
            if self.action == 'retrieve':
                queryset = queryset.prefetch_related('items')
            return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DisposalListSerializer
        elif self.action == 'retrieve':
            return DisposalSerializer
        return DisposalAddSerializer
    
    def get_serializer_context(self):
        user = self.request.user.id
        return {'pharmacy_pk':self.kwargs['pharmacy_pk'],'user': user}
    
    def get_permissions(self):
        if self.action == 'delete':
            return [permissions.IsAuthenticated(),ManagerOrPharmacyManagerPermission()]
        return [permissions.IsAuthenticated()]
    
    def destroy(self, request, *args, **kwargs):
        disposal = self.get_object()
        with transaction.atomic():
            disposal.items.all().delete()
            return super().destroy(request, *args, **kwargs)


class RetriveViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
            queryset = Returment.objects.prefetch_related('user').filter(pharmacy_id=self.kwargs['pharmacy_pk'])
            if self.action == 'retrieve':
                queryset = queryset.prefetch_related('items')
            return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return RetriveListSerializer
        elif self.action == 'retrieve':
            return RetriveSerializer
        return RetriveAddSerializer
    
    def get_serializer_context(self):
        user = self.request.user.id
        return {'pharmacy_pk':self.kwargs['pharmacy_pk'],'user': user}
    
    def get_permissions(self):
        if self.action == 'delete':
            return [permissions.IsAuthenticated(),ManagerOrPharmacyManagerPermission()]
        return [permissions.IsAuthenticated(),SalerPermission()]
    
    def destroy(self, request, *args, **kwargs):
        returment = self.get_object()
        with transaction.atomic():
            returment.items.all().delete()
            return super().destroy(request, *args, **kwargs)    


class NotificationList(mixins.ListModelMixin,viewsets.GenericViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(pharmacy_id=self.kwargs['pharmacy_pk'])



