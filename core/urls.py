from django.urls import path,include
from .views import *
urlpatterns = [
    path('medicine/<int:pk>',MedicineListCreateAPIView.as_view()),
    path('purchase/<int:pk>',PurchaseListCreateAPIView.as_view()),

]
