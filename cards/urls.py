from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CreditCardViewSet

router = DefaultRouter()
router.register(r'', CreditCardViewSet, basename='creditcard')

urlpatterns = [
    path('', include(router.urls)),
]

app_name = 'cards'