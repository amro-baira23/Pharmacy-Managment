from django.db.models import Q

from rest_framework import permissions

from core.models import Pharmacy

class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return request.user.is_owner
        
        
class PharmacyOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            id = view.kwargs.get("pharmacy_pk")
            return Pharmacy.objects.filter(owner_id=request.user.id,id=id).exists()

        
class PharmacyOwnerOrManager(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            id = view.kwargs.get("pharmacy_pk")
            return Pharmacy.objects.filter(Q(owner_id=request.user.id)|
                                        Q(employees__user_id=request.user.id,employees__role='M'),
                                        id=id).exists()
        

class IsMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            id = view.kwargs.get("pharmacy_pk")
            return Pharmacy.objects.filter(Q(owner_id=request.user.id)|Q(employees__user_id=request.user.id),id=id).exists()