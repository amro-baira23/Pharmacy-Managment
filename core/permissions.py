from django.db.models import Q

from rest_framework import permissions

from core.models import Pharmacy,Employee

class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return Pharmacy.objects.filter(owner_id=request.user.id).exists()
        

class PharmacyOwnerOrManager(permissions.BasePermission):
    def has_permission(self, request, view):
        id = view.kwargs.get("pharmacy_pk")
        return Pharmacy.objects.filter(Q(owner_id=request.user.id)|
                                       Q(employees__id=request.user.id,employees__role='M'),
                                       id=id).exists()


class isMember(permissions.BasePermission):
    def has_permission(self, request, view):
        pharma = Pharmacy.objects.get(id=view.kwargs['pk'])
        if pharma.owner_id == request.user.id:
            return True
        
        is_employee = Employee.objects.filter(pharmacy_id=view.kwargs['pk'],user_id=request.user.id).exists()
        
        return is_employee
