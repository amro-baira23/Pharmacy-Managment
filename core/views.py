from .models import *
from .serializers import *
from .permissions import *
from rest_framework import generics,authentication,viewsets,response


class MedicineViewset(viewsets.ModelViewSet):
    # permission_classes = [isMember]
    serializer_class = MedicineSerializer
    
    def get_queryset(self):
        return Medicine.objects.filter( pharmacy_id=self.kwargs['pharmacy_pk'])
    
   
class PurchaseViewset(viewsets.ModelViewSet):
    # permission_classes = [isMember]
    serializer_class = PurchaseSerializer

    def get_queryset(self):
        return Purchase.objects.filter( pharmacy_id=self.kwargs['pharmacy_pk'])
    
    def get_serializer_class(self):
        if self.action is 'list':
            return PurchaseListSerializer
        return PurchaseSerializer

    def perform_create(self, serializer):
        items = self.request.data.get('items')
        if not items:
            raise Exception("Purchase order can't be empty")
        instance = serializer.save(pharmacy_id = self.kwargs['pharmacy_pk'])
        purchase = Purchase.objects.get(id=instance.id)
        item_serializer = PurchaseItemSerializer(data=items,many=True)
        if  item_serializer.is_valid():
            item_serializer.save(purchase_id=purchase.id)
        serializer.save()






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
    

class PharmacyEmployeeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwner]

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
        return response.Response(status=200)
