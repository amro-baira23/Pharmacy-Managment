import io
from rest_framework import response
from rest_framework.decorators import action
from rest_framework.reverse import reverse_lazy,reverse
from rest_framework import mixins,viewsets,status

from django.db.models import Sum,Q
from django.http import FileResponse
from .pdf.create_pdf import create_pdf

from .models import EqualMedicine, Pharmacy
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
            date = {'date':str(date),'link':link}
            data.append(date)
            
        return response.Response(data)
    
    @action(detail=True,methods=['get'])
    def report(self,request,**kwargs):

        order = self.get_object()
        
        buffer = io.BytesIO()

        data = []
        for item in order.items.select_related("medicine").all():
            data.append([item.medicine.brand_name,item.price,item.quantity,item.price * item.quantity])
        
        pharmacy = Pharmacy.objects.get(id=kwargs['pharmacy_pk'])

        create_pdf(buffer,data,pharmacy,order.id)

        buffer.seek(0)

        return FileResponse(buffer,as_attachment=False,filename="report.pdf")


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
    

class ListCreateOnly(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet
                ):
    
    @action(detail=False,methods=['delete'])
    def remove(self,request,**kwargs):
        med_id = self.kwargs['medicine_pk']
        fil = Q(medicine1__id = med_id) | Q(medicine2__id = med_id)
        EqualMedicine.objects.filter(fil).delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)