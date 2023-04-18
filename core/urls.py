from django.urls import path,include
from .views import MedicineListCreateAPIView
urlpatterns = [
    path('medicine/<int:pk>',MedicineListCreateAPIView.as_view()),

]
