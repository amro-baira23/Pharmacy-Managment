from rest_framework.routers import DefaultRouter

from core.viewsets import *

router = DefaultRouter()
router.register('pharmacy/<int:pharmacy_id>/purchase/', GenericPurchaseViewSet, basename='purchase')

urlpatterns = router.urls

