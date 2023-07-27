from rest_framework import permissions

from core.models import Pharmacy

class ManagerOrPharmacyManagerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        roles = request.user.roles.values_list('role',flat=True)
        id = view.kwargs.get("pharmacy_pk") or view.kwargs.get("pk")
        if Pharmacy.objects.filter(id=id).exists():
            return 'manager' in roles or ('pharmacy_manager' in roles and request.user.pharmacy.id == int(id))
        return False
    
class SalerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        roles = request.user.roles.values_list('role',flat=True)
        id = view.kwargs.get("pharmacy_pk") or view.kwargs.get("pk")
        if Pharmacy.objects.filter(id=id).exists():
            return 'manager' in roles or (('pharmacy_manager' in roles or 'saller' in roles) and request.user.pharmacy.id == int(id))
        return False
    
class PurchasePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        roles = request.user.roles.values_list('role',flat=True)
        id = view.kwargs.get("pharmacy_pk") or view.kwargs.get("pk")
        if Pharmacy.objects.filter(id=id).exists():
            return 'manager' in roles or (('pharmacy_manager' in roles or 'purcher' in roles) and request.user.pharmacy.id == int(id))
        return False

class PharmacyManagerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        roles = request.user.roles.values_list('role',flat=True)
        return 'pharmacy_manager' in roles 

class ManagerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        roles = request.user.roles.values_list('role',flat=True)
        return 'manager' in roles or 'pharmacy_manager' in roles 
    
class GenralManagerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user_roles = request.user.roles.values_list('role',flat=True)
        return 'manager' in user_roles
    