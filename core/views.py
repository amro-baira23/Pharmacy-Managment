from django.utils.translation import gettext as _

from rest_framework import viewsets,response,status
from django.urls import reverse
from rest_framework.decorators import action
from django_filters import rest_framework as filters
from rest_framework import viewsets,response,status,mixins
from django.db.models import Case,When,F
from .models import *
from .serializers import *
from .permissions import *
from .mixins import *
from .filters import *

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
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class  = EmployeeFilter
    
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
    
    @action(detail=False,methods=['get'])
    def shifts(self, request, *args, **kwargs):
        shifts = Shift.objects.all().order_by('name')
        print(self.basename)
        api_root = reverse(f'core:{self.basename}-list',kwargs=kwargs,request=request) 
        
        data = []
        for shift in shifts:
            shift_name = shift.name.replace(' ','+')
            link = f"{api_root}?shift={shift_name}"
            item = {f'{shift.name}':link}
            data.append(item)

        return response.Response(data)
        

class UnactiveEmployeeViewSet(mixins.ListModelMixin,mixins.UpdateModelMixin,viewsets.GenericViewSet):
    http_method_names = ['get','patch','options']
    permission_classes = [permissions.IsAuthenticated,ManagerOrPharmacyManagerPermission]

    def partial_update(self, request, *args, **kwargs):
        request.data._mutable = True
        request.data.update({"is_active":True})
        return super().partial_update(request, *args, **kwargs)

    def get_queryset(self):
        queryset = User.objects.filter(pharmacy_id=self.kwargs['pharmacy_pk'],is_active=False)
        return queryset
        
    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer
        else:
            return UnactEmployeeUpdateSerializer
      
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
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class  = MedicineFilter
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

    @action(detail=False,methods=['get'])
    def companies(self,request,*args,**kwargs):
        companies = Company.objects.all().order_by('name')
        api_root = reverse(f'core:{self.basename}-list',kwargs=kwargs,request=request) 

        data = []
        for company in companies:
            link = f"{api_root}?company={company.name}"
            item = {f'{company.name}':link}
            data.append(item)

        return response.Response(data)
    
class InventoryViewset(mixins.ListModelMixin,viewsets.GenericViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class  = InventoryFilter
    serializer_class = MedicineListSerializer

    def get_queryset(self):
        purchase = PurchaseItem.objects.filter(purchase__pharmacy_id=self.kwargs["pharmacy_pk"],medicine_id=OuterRef('pk')).values('medicine').annotate(amount_sum=Sum('quantity')).values('amount_sum')
        sale = SaleItem.objects.filter(sale__pharmacy_id=self.kwargs["pharmacy_pk"],medicine_id=OuterRef('pk')).values('medicine').annotate(amount_sum=Sum('quantity')).values('amount_sum')
        dispose = DisposedItem.objects.filter(disposal__pharmacy_id=self.kwargs["pharmacy_pk"],medicine_id=OuterRef('pk')).values('medicine').annotate(amount_sum=Sum('quantity')).values('amount_sum')
        returment = ReturnedItem.objects.filter(returment__pharmacy_id=self.kwargs["pharmacy_pk"],medicine_id=OuterRef('pk')).values('medicine').annotate(amount_sum=Sum('quantity')).values('amount_sum')
        queryset = Medicine.objects.filter(purchase_items__purchase__pharmacy_id=self.kwargs["pharmacy_pk"]).distinct().annotate(quantity=Coalesce(Subquery(purchase),0)-Coalesce(Subquery(sale),0)-Coalesce(Subquery(dispose),0)+Coalesce(Subquery(returment),0))
        return queryset

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [ManagerPermission()]
    
    @action(detail=True,methods=["get"])
    def batches(self,request,*args,**kwargs):
        pharmacy_id = self.kwargs['pharmacy_pk']
        purchase = PurchaseItem.objects.filter(purchase__pharmacy_id=pharmacy_id,medicine_id=OuterRef('pk'),expiry_date=OuterRef("purchase_items__expiry_date")).values('medicine','expiry_date').annotate(amount_sum=Sum('quantity')).values('amount_sum')

        sale = SaleItem.objects.filter(sale__pharmacy_id=pharmacy_id,medicine_id=OuterRef('pk'),expiry_date=OuterRef("purchase_items__expiry_date")).values('medicine','expiry_date').annotate(amount_sum=Sum('quantity')).values('amount_sum')

        dispose = DisposedItem.objects.filter(disposal__pharmacy_id=pharmacy_id,medicine_id=OuterRef('pk'),expiry_date=OuterRef("purchase_items__expiry_date")).values('medicine','expiry_date').annotate(amount_sum=Sum('quantity')).values('amount_sum')

        returment = ReturnedItem.objects.filter(returment__pharmacy_id=pharmacy_id,medicine_id=OuterRef('pk'),expiry_date=OuterRef("purchase_items__expiry_date")).values('medicine','expiry_date').annotate(amount_sum=Sum('quantity')).values('amount_sum')

        batch = Medicine.objects.filter(id=self.kwargs['pk'],purchase_items__purchase__pharmacy_id=pharmacy_id).annotate(batch = F('purchase_items__expiry_date')).annotate(quantity=Coalesce(Subquery(purchase),0)-Coalesce(Subquery(sale),0)-Coalesce(Subquery(dispose),0)+Coalesce(Subquery(returment),0)).values("batch","quantity").distinct()
        return response.Response(batch)
    
class PurchaseViewset(StockListMixin,viewsets.ModelViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class  = StockFilter
    
    def get_queryset(self):
        queryset = Purchase.objects.select_related('reciver')\
        .filter(pharmacy_id=self.kwargs['pharmacy_pk'])
        if self.action == 'retrieve':
            queryset = queryset.prefetch_related('items')
        return queryset.annotate(value=Sum(F('items__quantity')*F('items__price')))
   
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

            _ ,amounts = purchase_exclude_amounts(purchase,items,pharmacy_id,True)

            for item in amounts:
                if 0 > item:
                    raise serializers.ValidationError({'error':'cant make this change some total amount will become negative'})
           
            items.delete()

        return super().destroy(request, *args, **kwargs)
      

class SaleViewset(StockListMixin,viewsets.ModelViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class  = StockFilter
    
    def get_queryset(self):
            queryset = Sale.objects.select_related('seller').filter(pharmacy_id=self.kwargs['pharmacy_pk'])
            if self.action == 'retrieve':
                queryset = queryset.prefetch_related('items')
            return queryset.annotate(value=Sum(F('items__quantity')*F('items__price')))
    
    def get_serializer_class(self):
        if self.action in ['list']:
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
        

class DisposalViewSet(StockListMixin,viewsets.ModelViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class  = StockFilter
    
    def get_queryset(self):
            queryset = Disposal.objects.select_related('user').filter(pharmacy_id=self.kwargs['pharmacy_pk'])
            if self.action == 'retrieve':
                queryset = queryset.prefetch_related('items')
            return queryset.annotate(value=Sum(F('items__quantity')*F('items__price')))
    
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


class RetriveViewSet(StockListMixin,viewsets.ModelViewSet):
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class  = StockFilter
    
    def get_queryset(self):
            queryset = Returment.objects.select_related('user').filter(pharmacy_id=self.kwargs['pharmacy_pk'])
            if self.action == 'retrieve':
                queryset = queryset.prefetch_related('items')
            return queryset.annotate(value=Sum(F('items__quantity')*F('items__price')))

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
        

class TransactionViewset(MultipleStockListMixin):
        filter_backends = (filters.DjangoFilterBackend,)
        filterset_class = StockFilter 
        
        def get_querylist(self):
            querylist = [
            {'queryset': Purchase.objects.all().filter(pharmacy_id=self.kwargs['pharmacy_pk'])},
            {'queryset': Sale.objects.all().filter(pharmacy_id=self.kwargs['pharmacy_pk'])},
            {'queryset': Returment.objects.all().filter(pharmacy_id=self.kwargs['pharmacy_pk'])},
            ]
            return querylist
        

class NotificationList(mixins.ListModelMixin,viewsets.GenericViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(pharmacy_id=self.kwargs['pharmacy_pk'])

        
class EqualViewSet(ListCreateOnly):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        med_id = self.kwargs['medicine_pk']
        fil = Q(medicine1__id = med_id) | Q(medicine2__id = med_id)

        subquery = EqualMedicine.objects.filter(fil).annotate(medicine=Case(
                                            When(medicine1 = med_id, then=F("medicine2")),
                                            When(medicine2 = med_id, then=F("medicine1")),
                                         )).values('medicine')

        return Medicine.objects.filter(id__in=Subquery(subquery)).values('id','brand_name')

    def get_serializer_class(self):
        if self.action == 'create':
            return EqualsCreateSerializer
        return MedicineEqualListSerializer

    def get_serializer_context(self):
        return {'medicine':int(self.kwargs['medicine_pk'])}