from django.db.models import Q

from rest_framework import permissions

from core.models import Pharmacy

#class IsOwner(permissions.BasePermission):
#    def has_permission(self, request, view):
#        if request.user and request.user.is_authenticated:
#            return request.user.is_owner
        
        
#class PharmacyOwner(permissions.BasePermission):
#    def has_permission(self, request, view):
#        if request.user and request.user.is_authenticated:
#            id = view.kwargs.get("pharmacy_pk")
#            return request.user.is_owner and Pharmacy.objects.filter(pk=id).exists()

        
#class EmployeePermission(permissions.BasePermission):
#    def has_permission(self, request, view):
#        if request.user and request.user.is_authenticated:
#            id = view.kwargs.get("pharmacy_pk") or view.kwargs.get("pk")
#            pharmacy = Pharmacy.objects.filter(id=id)
#            if pharmacy.exists():
#                return request.user.is_owner or \
#                    bool ((request.user.pharmacy.id == int(id) or
#                           request.user.has_perm("core.add_pharmacy")) and \
#                            request.user.has_perm('custom.add_user')) 
#                    
#
#class IsMember(permissions.BasePermission):
#    def has_permission(self, request, view):
#        if request.user and request.user.is_authenticated:
#            id = view.kwargs.get("pharmacy_pk") or view.kwargs.get("pk")
#            pharmacy = Pharmacy.objects.filter(id=id)
#            if pharmacy.exists():
#                return request.user.is_owner or bool (request.user.pharmacy.id == int(id))     

class ManagerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user_roles = request.user.roles.values_list('role',flat=True)
        if 'manager' in user_roles:
            return True
        
        if 'pharmacy_manager' in user_roles:
            id = view.kwargs.get("pharmacy_pk") or view.kwargs.get("pk")
            if Pharmacy.objects.filter(id=id).exists():
                return request.user.pharmacy.id == int(id)


class GenralManagerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user_roles = request.user.roles.values_list('role',flat=True)
        if 'manager' in user_roles:
            return True