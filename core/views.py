from rest_framework import viewsets,response,status
from django.utils.translation import gettext as _

from .models import *
from .serializers import *
from .permissions import *

class PharmacyViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        user = self.request.user
        if 'manager' in user.roles.values_list('role',flat=True):
            return Pharmacy.objects.all()
        return Pharmacy.objects.filter(id=user.pharmacy_id)

    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(),ManagmentPermission()]


    def get_serializer_class(self):
        if self.action == 'list':
            return PharmacyListSerializer
        return PharmacySerializer
    
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
    permission_classes = [permissions.IsAuthenticated,ManagmentPermission]
    http_method_names = ['get','put','delete','post']

    def get_queryset(self):
        return User.objects.prefetch_related('roles').filter(pharmacy_id=self.kwargs['pharmacy_pk'],is_active=True)
    
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
    

#class MedicineViewset(viewsets.ModelViewSet):
#    
#    def get_permissions(self):
#        if self.request.method == 'GET':
#            return [IsMember()]
#        return [EmployeePermission()]
#        
#    def get_queryset(self):
#        return Medicine.objects.all()
#    
#    def get_serializer_class(self):
#        if self.action == 'update' or self.action == 'partial_update':
#            return MedicineUpdateSerializer
#        if self.action == 'create':
#            return MedicineCreateSerializer
#        return MedicineListSerializer
#         
#    def destroy(self, request, *args, **kwargs):
#        instance = self.get_object()
#        if SaleItem.objects.filter(medicine=instance).exists():
#            return response.Response({'error':_('cant delete a medicine which sold once but you can archive it')})
#        instance.delete()
#        return response.Response(status=status.HTTP_204_NO_CONTENT)

#
#class PurchaseViewset(viewsets.ModelViewSet):
#    permission_classes = [PharmacyOwnerOrManager]
#    serializer_class = PurchaseSerializer
#
#    def get_queryset(self):
#        return Purchase.objects.filter(pharmacy_id=self.kwargs['pharmacy_pk'])
#    
#    def get_serializer_class(self):
#        if self.action == 'list':
#            return PurchaseListSerializer
#        elif self.action == 'create':
#            return PurchaseCreateSerializer
#        return PurchaseSerializer
#    
#    def get_serializer_context(self):
#        user = self.request.user
#        name = user.first_name + ' ' + user.last_name
#        return {'pharmacy_pk':self.kwargs['pharmacy_pk'],'name':name}
#
#    def perform_create(self, serializer):
#        items = self.request.data.get('items')
#
#        for item in items:
#            for idx2,item2 in enumerate(items):
#                if item['medicine'] == item2['medicine'] and item is not item2:
#                    item['quantity'] += item2['quantity']
#                    items.pop(idx2)
#
#
#        with transaction.atomic():
#            purchase = serializer.save()
#            new_context = {'purchase':purchase,'pharmacy_pk':self.kwargs['pharmacy_pk']}
#            item_serializer = PurchaseItemSerializer(data=items,many=True,context=new_context)
#            item_serializer.is_valid(raise_exception=True)
#            item_serializer.save()
#
#
#class SaleViewset(viewsets.ModelViewSet):
#
#    def get_queryset(self):
#            if self.action == 'list':
#                 return Sale.objects.filter(pharmacy_id=self.kwargs['pharmacy_pk'])
#            return Sale.objects.prefetch_related('items').filter(pharmacy_id=self.kwargs['pharmacy_pk'])
#    
#    def get_serializer_class(self):
#        if self.action == 'list':
#            return SaleListSerializer
#        elif self.action == 'retrieve':
#            return SaleSerizlizer
#        return SaleCreateSerializer
#    
#    def get_serializer_context(self):
#        user = self.request.user
#        name = user.first_name + ' ' + user.last_name
#        return {'pharmacy_pk':self.kwargs['pharmacy_pk'],'name':name}
#    
#    def get_permissions(self):
#        if self.action == 'delete':
#            return [PharmacyOwner()]
#        return [IsMember()]
#
#
#    def perform_create(self, serializer):
#        items = serializer.validated_data['items']
#
#        with transaction.atomic():
#            sale = serializer.save()
#            new_context = {'sale':sale,'pharmacy_pk':self.kwargs['pharmacy_pk']}
#            item_serializer = SaleItemSerializer(data=items,many=True,context=new_context)
#            if not item_serializer.is_valid():
#                raise serializers.ValidationError({'error':_('some items are invalid')})
#            item_serializer.save()
#
#
