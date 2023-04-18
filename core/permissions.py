from rest_framework import permissions
from core.models import Pharmacy,Employee



class isMember(permissions.BasePermission):
    def has_permission(self, request, view):
        pharma = Pharmacy.objects.get(id=view.kwargs['pk'])
        if pharma.owner_id == request.user.id:
            return True
        
        is_employee = Employee.objects.filter(pharmacy_id=view.kwargs['pk'],user_id=request.user_id).exists()
        
        return is_employee
