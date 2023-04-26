from .models import *
from .serializers import *
from .permissions import *
from rest_framework import viewsets,response,status


class MedicineViewset(viewsets.ModelViewSet):
    permission_classes = [IsMember]

    def get_queryset(self):
        return Medicine.objects.select_related('company').filter(pharmacy_id=self.kwargs['pharmacy_pk'],is_active=1)
    
    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'partial_update':
            return MedicineUpdateSerializer
        return MedicineSerializer

    def get_serializer_context(self):
        return {'pharmacy_pk':self.kwargs['pharmacy_pk']}
         
   
class PurchaseViewset(viewsets.ModelViewSet):
    permission_classes = [PharmacyOwnerOrManager]
    serializer_class = PurchaseSerializer

    def get_queryset(self):
        return Purchase.objects.filter( pharmacy_id=self.kwargs['pharmacy_pk'])
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PurchaseListSerializer
        return PurchaseSerializer

    def perform_create(self, serializer):
        items = self.request.data.get('items')
        if not items:
            raise Exception("purchase order can't be empty")
        purchase = serializer.save(pharmacy_id = self.kwargs['pharmacy_pk'])
        item_serializer = PurchaseItemSerializer(data=items,many=True,context={'purchase':purchase})
        if  item_serializer.is_valid(raise_exception=True):
            
            item_serializer.save(purchase_id=purchase.id)
        serializer.save()


class SaleViewset(viewsets.ModelViewSet):

    def get_queryset(self):
            if self.action == 'list':
                 return Sale.objects.filter(pharmacy_id=self.kwargs['pharmacy_pk'])
            return Sale.objects.prefetch_related('items').filter(pharmacy_id=self.kwargs['pharmacy_pk'])
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SaleListSerializer
        elif self.action == 'retrieve':
            return SaleSerizlizer
        return SaleCreateSerializer
    
    def get_serializer_context(self):
        user = self.request.user
        name = user.first_name + ' ' + user.last_name
        return {'pharmacy_pk':self.kwargs['pharmacy_pk'],'name':name}
    
    def get_permissions(self):
        if self.action == 'delete':
            return [PharmacyOwner()]
        return [IsMember()]


    def perform_create(self, serializer):
        items = self.request.data.get('items')

        for item in items:
            for idx2,item2 in enumerate(items):
                if item['medicine'] == item2['medicine'] and item is not item2:
                    item['quantity'] += item2['quantity']
                    items.pop(idx2)

        with transaction.atomic():
            sale = serializer.save()
            new_context = {'sale':sale,'pharmacy_pk':self.kwargs['pharmacy_pk']}
            item_serializer = SaleItemSerializer(data=items,many=True,context=new_context)
            item_serializer.is_valid(raise_exception=True)
            item_serializer.save()


class PharmacyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwner]

    def get_queryset(self):
        return Pharmacy.objects.filter(owner_id=self.request.user.id)

    def get_serializer_class(self):
        if self.action == 'list':
            return PharmacyListSerializer
        return PharmacySerializer
    
    def get_serializer_context(self):
        return {'owner_id':self.request.user.id}
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        count = Pharmacy.objects.filter(owner_id=request.user.id).count()
        if count == 1:
            return response.Response({"error":"cant delete when you only have one"})
        instance.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
    

class PharmacyEmployeeViewSet(viewsets.ModelViewSet):
    permission_classes = [PharmacyOwner]

    def get_queryset(self):
        return Employee.objects.select_related('user').filter(pharmacy_id=self.kwargs['pharmacy_pk'])
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer
        if self.action == 'create':
            return EmployeeCreateSerializer
        return EmployeeSerializer
    
    def get_serializer_context(self):
        return {'pharmacy_pk':self.kwargs['pharmacy_pk']}
    

    def destroy(self, request, *args, **kwargs):
        user_id = self.get_object().user_id
        User.objects.get(id=user_id).delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
