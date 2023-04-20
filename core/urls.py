from django.urls import path,include
from .views import *
from .viewsets import *
urlpatterns = [
    path('medicine/<int:pharmacy_id>/medicine/<int:medicine_id>',MedicineListCreateAPIView.as_view()),
    path('pharmacy/<int:pharmacy_id>/purchase/',purchase_list_view),
    path('pharmacy/<int:pharmacy_id>/purchase/<int:pk>',PurchaseRetrieveDestroyUpdateAPIView.as_view()),

]
