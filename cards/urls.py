from django.urls import path
from .views import (
    CreditCardListCreateView,
    CreditCardDetailView, CreditCardStatusUpdateView, CreditCardLimitUpdateView,
)

urlpatterns = [
    path('', CreditCardListCreateView.as_view(), name='card-list-create'),
    path('<int:pk>/', CreditCardDetailView.as_view(), name='card-detail'),
    path('<int:pk>/update-status/', CreditCardStatusUpdateView.as_view(), name='card-status-update'),
    path('<int:pk>/update-limit/', CreditCardLimitUpdateView.as_view(), name='card-limit-update'),
]
