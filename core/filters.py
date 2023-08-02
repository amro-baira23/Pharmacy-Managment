
from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters
from core.models import *
from core.statics import TYPE_CHOICES,roles_map

User = get_user_model()

class MedicineFilter(filters.FilterSet):
    brand_name = filters.CharFilter(field_name='brand_name',lookup_expr='icontains',label='brand_name')
    company = filters.CharFilter(field_name='company__name',lookup_expr='icontains',label='company')
    ordering = filters.OrderingFilter(fields=(('amount','quantity'),))
                                      
    class Meta:
        model = Medicine
        fields = ['type','barcode']        


class StockFilter(filters.FilterSet):
    date = filters.DateRangeFilter(field_name='time_stamp')
    since = filters.DateFilter(field_name='time_stamp',lookup_expr='gte')
    before = filters.DateFilter(field_name='time_stamp',lookup_expr='lt')
    ordering = filters.OrderingFilter(fields=('value','time_stamp'))



class EmployeeFilter(filters.FilterSet):
    first_name = filters.CharFilter(field_name='first_name',lookup_expr='icontains')
    last_name = filters.CharFilter(field_name='last_name',lookup_expr='icontains')
    shift = filters.CharFilter(field_name='shift__name',lookup_expr='exact')
    ordering = filters.OrderingFilter(fields=('first_name','salry'))
    class Meta:
        model = User
        fields = ['roles__role']


