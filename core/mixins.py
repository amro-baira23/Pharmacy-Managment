from rest_framework import response,mixins,viewsets
from rest_framework.decorators import action
from rest_framework.reverse import reverse
from django.db.models.functions import Coalesce
from django.db.models import Sum,F,Value

from .models import *

class StockListMixin:
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        
        serializer = self.get_serializer(queryset, many=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)


        value = queryset.aggregate(value=Coalesce(Sum(F('items__quantity')*F('items__price')),Value(0)))['value'] 
        data = {"data":serializer.data,"value":value}
     
        return response.Response(data)
    
    @action(detail=False,methods=['get'])
    def months(self,request,**kwargs):
        queryset = self.get_queryset()
        dates = queryset.dates(field_name='time_stamp',kind='month') 
        api_root = reverse(f'core:{self.basename}-list',kwargs=kwargs,request=request) 

        data = []
        for i,date in enumerate(dates):
            after_month = dates[i+1] if i < dates.count() - 1 else ""
            link = api_root + f'?since={date}&before={after_month}'
            date = {'date':str(date),'link':link}
            data.append(date)
            
        return response.Response(data)


class MultipleStockListMixin(mixins.ListModelMixin,viewsets.GenericViewSet):

    def list(self, request, *args, **kwargs):
        querylist = self.get_querylist()

        for query_data in querylist:
            query_data['queryset'] = self.filter_queryset(query_data['queryset'])

        trans = ['purchase','sale','retrieve']

        temp = {}
        for i,qs in enumerate(querylist):
            qs = qs['queryset'].aggregate(value=Coalesce(Sum(
            F('items__quantity')*F('items__price')),Value(0)))
            temp[trans[i]] = qs['value']

        data = {}
        data['income'] = temp['sale'] - temp['retrieve']
        data['outcome'] = temp['purchase']
        data['total_profit'] = data['income'] - data['outcome']

        return response.Response(data)
    

    @action(detail=False,methods=['get'])
    def months(self,request,**kwargs):
        querylist = self.get_querylist()
        queryset = querylist[0]['queryset']
        dates = queryset.dates(field_name='time_stamp',kind='month') 
        api_root = reverse(f'core:{self.basename}-list',kwargs=kwargs,request=request) 

        data = []
        for i,date in enumerate(dates):
            after_month = dates[i+1] if i < dates.count() - 1 else ""
            link = api_root + f'?since={date}&before={after_month}'
            date = {'month': str(date),'link': link}
            data.append(date)

        return response.Response(data)
    
    #returns an empty queryset to avoid and error
    def get_queryset(self):
        return Purchase.objects.none()
        
