from .models import *
from rest_framework import viewsets,mixins
from .serializers import *


class GenericPurchaseViewSet(mixins.ListModelMixin,mixins.RetrieveModelMixin,mixins.DestroyModelMixin,mixins.UpdateModelMixin,viewsets.GenericViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    lookup_field= 'pk'


purchase_list_view = GenericPurchaseViewSet.as_view({'get': 'list'})
product_detail_view = GenericPurchaseViewSet.as_view({'patch': 'partial_update'})