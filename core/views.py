from rest_framework import viewsets,response,status
from django.utils.translation import gettext as _

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
            return queryset.select_related('shift').prefetch_related('roles','shift__days')
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
        if self.action in ['create','update','partial_update']:
            return ShiftAddSerializer
        elif self.action == 'retrieve':
            return ShiftSerializer
        return ShiftListSerializer
    
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
    queryset = Medicine.objects.all()
    
    
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
       elif self.action == 'create':
           return PurchaseCreateSerializer
       elif self.action == 'update':
           return PurchaseUpdateSerializer
       elif self.action == 'partial_update':
           return PurchaseUpdateSerializer
       return PurchaseSerializer
   
   def get_serializer_context(self):
       user = self.request.user
       reciver = user.id
       return {'pharmacy_pk':self.kwargs['pharmacy_pk'],'reciver':reciver}

   def perform_create(self, serializer):
       items = self.request.data.get('items')
       for item in items:
           for idx2,item2 in enumerate(items):
               if item['medicine'] == item2['medicine'] and item is not item2:
                   item['quantity'] += item2['quantity']
                   items.pop(idx2)


       with transaction.atomic():
           purchase = serializer.save()
           new_context = {'purchase':purchase,'pharmacy_pk':self.kwargs['pharmacy_pk']}
           item_serializer = PurchaseItemSerializer(data=items,many=True,context=new_context)
           if not item_serializer.is_valid(raise_exception=True):
               raise serializers.ValidationError({'error':_('some items are invalid')})
           item_serializer.save()


class SaleViewset(viewsets.ModelViewSet):

   def get_queryset(self):
           if self.action == 'list':
                return Sale.objects.filter(pharmacy_id=self.kwargs['pharmacy_pk'])
           return Sale.objects.prefetch_related('items').filter(pharmacy_id=self.kwargs['pharmacy_pk'])
   
   def get_serializer_class(self):
       if self.action == 'list':
           return SaleListSerializer
       elif self.action == 'create':
           return SaleCreateSerializer
       elif self.action == 'update' :
           return SaleUpadateSerializer
       elif self.action == 'partial_update' :
           return SaleUpadateSerializer
       return SaleSerializer
   
   def get_serializer_context(self):
       user = self.request.user
       seller = user.id
       return {'pharmacy_pk':self.kwargs['pharmacy_pk'],'seller': seller}
   
#    def get_permissions(self):
#        if self.action == 'delete':
#            return [PharmacyOwner()]
#        return [IsMember()]


   def perform_create(self, serializer):
       items = serializer.validated_data['items']
       print(items) 
       for item in items:
           for idx2,item2 in enumerate(items):
               if item['medicine'] == item2['medicine'] and item is not item2:
                   item['quantity'] += item2['quantity']
                   items.pop(idx2)
 
       
       with transaction.atomic():
           sale = serializer.save()
           new_context = {'sale':sale,'pharmacy_pk':self.kwargs['pharmacy_pk']}
           item_serializer = SaleItemSerializer(data=items,many=True,context=new_context)
           if not item_serializer.is_valid():
               raise serializers.ValidationError({'error':_('some items are invalid')})
           item_serializer.save()


