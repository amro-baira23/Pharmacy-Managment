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

pharmacy_router.register('dispose',DisposalViewSet,basename='pharmacy-dispose')

pharmacy_router.register('retrive',RetriveViewSet,basename='pharmacy-retrive')

pharmacy_router.register('unactive_employee',UnactiveEmployeeViewSet,basename='pharmacy-unactive_employee')

pharmacy_router.register('transaction',TransactionViewset,basename='transaction')

urls = router.urls + pharmacy_router.urls

urlpatterns = urls
