from django.urls import path
from .views import *


from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('pharmacys',PharmacyViewSet,basename='pharmacya')

employee_router = routers.NestedDefaultRouter(router,'pharmacys',lookup='pharmacy')
employee_router.register('employee',PharmacyEmployeeViewSet,basename='pharmacy-employees')

medicine_router = routers.NestedDefaultRouter(router,'pharmacys',lookup='pharmacy')
medicine_router.register('medicine',MedicineViewset,basename='pharmacy-medicine')

purchase_router = routers.NestedDefaultRouter(router,'pharmacys',lookup='pharmacy')
purchase_router.register('purchase',PurchaseViewset,basename='pharmacy-medicine')

urls = router.urls + employee_router.urls + medicine_router.urls + purchase_router.urls

urlpatterns = urls
