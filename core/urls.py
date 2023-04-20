from django.urls import path
from .views import *
<<<<<<< HEAD
from .viewsets import *
urlpatterns = [
    path('medicine/<int:pharmacy_id>/medicine/<int:medicine_id>',MedicineListCreateAPIView.as_view()),
    path('pharmacy/<int:pharmacy_id>/purchase/',purchase_list_view),
    path('pharmacy/<int:pharmacy_id>/purchase/<int:pk>',PurchaseRetrieveDestroyUpdateAPIView.as_view()),
=======
>>>>>>> ef5ac64ea7975fd2b9461d1529dfb9da3fb35325

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
