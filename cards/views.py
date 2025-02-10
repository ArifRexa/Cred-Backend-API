from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import CreditCard
from .serializers import (
    CreditCardApplicationSerializer,
    CreditCardDetailSerializer,
    CardApplicationActionSerializer
)
from .permissions import IsAdminOrManager, IsAdminOrManagerOrOwner, IsAdmin
from .services import CardNumberGenerator


class CreditCardViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminOrManagerOrOwner]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'MANAGER']:
            return CreditCard.objects.all()
        return CreditCard.objects.filter(user=user)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreditCardApplicationSerializer
        return CreditCardDetailSerializer

    @extend_schema(
        tags=['Credit Cards'],
        description='Submit a new credit card application'
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Generate unique card number
        card_number = CardNumberGenerator.generate_unique_number(
            serializer.validated_data.get('card_type', 'VISA')
        )

        credit_card = serializer.save(
            user=request.user,
            card_number=card_number,
            status='PENDING'
        )

        return Response(
            self.get_serializer(credit_card).data,
            status=status.HTTP_201_CREATED
        )

    @extend_schema(
        tags=['Credit Cards'],
        description='Approve a credit card application',
        request=CardApplicationActionSerializer
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminOrManager])
    def approve(self, request, pk=None):
        credit_card = self.get_object()

        if credit_card.status != 'PENDING':
            return Response(
                {'error': 'Only pending applications can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )

        credit_card.status = 'APPROVED'
        credit_card.approved_by = request.user
        credit_card.save()

        return Response(
            self.get_serializer(credit_card).data,
            status=status.HTTP_200_OK
        )

    @extend_schema(
        tags=['Credit Cards'],
        description='Reject a credit card application',
        request=CardApplicationActionSerializer
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminOrManager])
    def reject(self, request, pk=None):
        credit_card = self.get_object()
        serializer = CardApplicationActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if credit_card.status != 'PENDING':
            return Response(
                {'error': 'Only pending applications can be rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )

        credit_card.status = 'REJECTED'
        credit_card.rejection_reason = serializer.validated_data.get('rejection_reason')
        credit_card.save()

        return Response(
            self.get_serializer(credit_card).data,
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        if request.user.role != 'ADMIN':
            return Response(
                {'error': 'Only admin can delete applications'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)
