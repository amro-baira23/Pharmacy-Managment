from .views import *
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('pharmacy',PharmacyViewSet,basename='pharmacy')

router.register('shift',ShiftViewSet,basename='shift')

router.register('company',CompanyViewSet,basename='company')

employee_router = routers.NestedDefaultRouter(router,'pharmacy',lookup='pharmacy')
employee_router.register('employee',PharmacyEmployeeViewSet,basename='pharmacy-employees')

#medicine_router = routers.NestedDefaultRouter(router,'pharmacy',lookup='pharmacy')
#medicine_router.register('medicine',MedicineViewset,basename='pharmacy-medicine')

#purchase_router = routers.NestedDefaultRouter(router,'pharmacy',lookup='pharmacy')
#purchase_router.register('purchase',PurchaseViewset,basename='pharmacy-purchase')
#
#sale_router = routers.NestedDefaultRouter(router,'pharmacy',lookup='pharmacy')
#sale_router.register('sale',SaleViewset,basename='pharmacy-sale')

#sale_item_router = routers.NestedDefaultRouter(sale_router,'sale',lookup='sale')
#sale_item_router.register('items',SaleViewset,basename='pharmacy-sale-items')

urls = router.urls  + employee_router.urls # + medicine_router.urls #+ purchase_router.urls + sale_router.urls #+ sale_item_router.urls

urlpatterns = urls
