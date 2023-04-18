from rest_framework import permissions
from core.models import Pharmacy,Employee
class isMember(permissions.BasePermission):
    def has_permission(self, request, view):
        pharma = Pharmacy.objects.get(id=view.kwargs['pk'])
        if pharma.owner_id == request.user.id:
            return True
        

        employees = Employee.objects.all().filter(pharmacy_id=view.kwargs['pk']).filter(id=request.user.id)
        if employees.exists():
            return True

        return False

    def has_object_permission(self, request, view, obj):
        print('hi')
        return False