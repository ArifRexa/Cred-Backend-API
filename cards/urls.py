from django.urls import path
from .views import (
    CreditCardListCreateView,
    CreditCardDetailView, CreditCardStatusUpdateView,
)

urlpatterns = [
    path('', CreditCardListCreateView.as_view(), name='card-list-create'),
    path('<int:pk>/', CreditCardDetailView.as_view(), name='card-detail'),
    path('cards/<int:pk>/update-status/', CreditCardStatusUpdateView.as_view(), name='card-status-update'),
]
