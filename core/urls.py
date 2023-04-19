from django.urls import path
from .views import *

from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('pharmacys',PharmacyViewSet,basename='pharmacya')

employee_router = routers.NestedDefaultRouter(router,'pharmacys',lookup='pharmacy')
employee_router.register('employee',PharmacyEmployeeViewSet,basename='pharmacy-employees')

urls = router.urls + employee_router.urls

urlpatterns = [
    path('medicine/<int:pk>/',MedicineListCreateAPIView.as_view()),
    path('purchase/<int:pk>/',PurchaseListCreateAPIView.as_view()),
] + urls
