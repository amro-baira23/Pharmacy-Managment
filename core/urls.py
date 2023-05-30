from .views import *
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('pharmacy',PharmacyViewSet,basename='pharmacy')

router.register('shift',ShiftViewSet,basename='shift')

router.register('company',CompanyViewSet,basename='company')

router.register('medicine',MedicineViewset,basename='medicine')

pharmacy_router = routers.NestedDefaultRouter(router,'pharmacy',lookup='pharmacy')

pharmacy_router.register('employee',PharmacyEmployeeViewSet,basename='pharmacy-employees')

pharmacy_router.register('purchase',PurchaseViewset,basename='pharmacy-purchase')

pharmacy_router.register('sale',SaleViewset,basename='pharmacy-sale')

pharmacy_router.register('dispose',DisposalViewSet,basename='pharmacy-dispse')


# sale_item_router = routers.NestedDefaultRouter(sale_router,'sale',lookup='sale')
# sale_item_router.register('items',SaleViewset,basename='pharmacy-sale-items')

urls = router.urls + pharmacy_router.urls #+ sale_item_router.urls

urlpatterns = urls
