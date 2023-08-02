from django.contrib import admin
from django.urls import path,include
import debug_toolbar

from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet

from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register('devices', FCMDeviceAuthorizedViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/',include('custom.urls')),
    path('api/auth/',include('djoser.urls.jwt')),
    path('__debug__/', include(debug_toolbar.urls)),
    path('api/',include('core.urls')),
    path('api/', include(router.urls)),
]
