from rest_framework import response
from rest_framework.decorators import action
from rest_framework.reverse import reverse_lazy,reverse
from django.db.models.functions import Coalesce
from django.db.models import Sum,ExpressionWrapper,F,Value

from .models import *
import datetime as dt

class StockListMixin:
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        value = queryset.aggregate(value=Coalesce(Sum(F('items__quantity')*F('items__price')),Value(0)))['value'] 
        data = {"data":serializer.data,"value":value}
     
        return response.Response([data])
    
    @action(detail=False,methods=['get'])
    def months(self,request,**kwargs):
        queryset = self.get_queryset()
        dates = queryset.dates(field_name='time_stamp',kind='month') 
        api_root = reverse(f'core:{self.basename}-list',kwargs=kwargs,request=request) 

        data = []
        for i,date in enumerate(dates):
            after_month = dates[i+1] if i < dates.count() - 1 else ""
            link = api_root + f'?since={date}&before={after_month}'
            date = {str(date):link}
            data.append(date)
            
        return response.Response(data)


class MultipleStockListMixin:

    def list(self, request, *args, **kwargs):
        querylist = self.get_querylist()

        for query_data in querylist:
            self.check_query_data(query_data)
            query_data['queryset'] = self.filter_queryset(query_data['queryset'])
            queryset = self.load_queryset(query_data, request, *args, **kwargs)

        trans = ['purchase','sale','retrieve','disposal']
        data = {}
        for i,qs in enumerate(querylist):
            qs = qs['queryset'].aggregate(value=Coalesce(Sum(
            F('items__quantity')*F('items__price')),Value(0)))
            data[trans[i]] = qs['value']

        data['summed_value'] = (data['sale'] + data['retrieve']) - (data['purchase'] + data['disposal'])

        return response.Response(data)
    

    @action(detail=False,methods=['get'])
    def months(self,request,**kwargs):
        querylist = self.get_querylist()
        queryset = querylist[0]['queryset']
        dates = queryset.dates(field_name='time_stamp',kind='month') 
        api_root = reverse_lazy(f'core:{self.basename}-list',kwargs=kwargs,request=request) 

        data = []
        for i,date in enumerate(dates):
            after_month = dates[i+1] if i < dates.count() - 1 else ""
            link = api_root + f'?since={date}&before={after_month}'
            date = {str(date):link}
            data.append(date)

        data = {'links':data}
        return response.Response(data)
