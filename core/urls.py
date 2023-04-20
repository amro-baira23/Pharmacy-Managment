from django.urls import path
from .views import *
from .viewsets import *


from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('pharmacys',PharmacyViewSet,basename='pharmacya')

employee_router = routers.NestedDefaultRouter(router,'pharmacys',lookup='pharmacy')
employee_router.register('employee',PharmacyEmployeeViewSet,basename='pharmacy-employees')

urls = router.urls + employee_router.urls

urlpatterns = [
    path('medicine/<int:pharmacy_id>/medicine/<int:medicine_id>',MedicineListCreateAPIView.as_view()),
    path('pharmacy/<int:pharmacy_id>/purchase/',PurchaseListCreateAPIView.as_view()),
    path('pharmacy/<int:pharmacy_id>/purchase/<int:pk>',PurchaseRetrieveDestroyUpdateAPIView.as_view()),
] + urls
