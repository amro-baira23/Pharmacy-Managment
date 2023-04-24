from django.contrib import admin
from django.urls import path,include
import debug_toolbar

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/',include('custom.urls')),
    path('api/auth/',include('djoser.urls.jwt')),
    path('__debug__/', include(debug_toolbar.urls)),
    path('api/',include('core.urls')),
]
