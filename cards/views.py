from django.http import Http404
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import JSONParser, MultiPartParser
from .models import CreditCard
from .serializers import (
    CreditCardApplicationSerializer,
    CreditCardDetailSerializer, CardStatusUpdateSerializer
)
from .permissions import IsAdminOrManager, IsAdminOrManagerOrOwner
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample


class CreditCardListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrManagerOrOwner]
    parser_classes = (MultiPartParser, JSONParser,)
    serializer_class = CreditCardApplicationSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'MANAGER']:
            return CreditCard.objects.all()
        return CreditCard.objects.filter(user=user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreditCardApplicationSerializer
        return CreditCardDetailSerializer

    @extend_schema(
        tags=['Credit Cards'],
        description='List all credit cards or create a new application'
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=['Credit Cards'],
        description='Submit a new credit card application'
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Create card instance but don't save yet
            credit_card = CreditCard(
                user=request.user,
                card_type=serializer.validated_data.get('card_type', 'VISA'),
                credit_limit=serializer.validated_data.get('credit_limit'),
                status='PENDING'
            )
            # Save will trigger the card number generation and validation
            credit_card.save()

            return Response(
                self.get_serializer(credit_card).data,
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return Response(
                {'error': str(e.messages[0]) if hasattr(e, 'messages') else str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'An unexpected error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CreditCardDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrManagerOrOwner]
    parser_classes = (MultiPartParser, JSONParser,)
    serializer_class = CreditCardDetailSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'MANAGER']:
            return CreditCard.objects.all()
        return CreditCard.objects.filter(user=user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CreditCardApplicationSerializer
        return CreditCardDetailSerializer

    @extend_schema(
        tags=['Credit Cards'],
        description='Delete a credit card application'
    )
    def delete(self, request, *args, **kwargs):
        if request.user.role != 'ADMIN':
            return Response(
                {'error': 'Only admin can delete applications'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().delete(request, *args, **kwargs)


class CreditCardStatusUpdateView(APIView):
    permission_classes = [IsAdminOrManager]
    parser_classes = (JSONParser, MultiPartParser,)
    serializer_class = CardStatusUpdateSerializer

    def get_object(self, pk):
        try:
            return CreditCard.objects.get(pk=pk)
        except CreditCard.DoesNotExist:
            raise Http404

    @extend_schema(
        tags=['Credit Cards'],
        description='Update credit card application status (Admin/Manager only)',
        request=CardStatusUpdateSerializer,
        responses={
            200: CreditCardDetailSerializer,
            400: OpenApiResponse(
                description='Bad request - Invalid data or card not in pending status'
            ),
            401: OpenApiResponse(description='Authentication credentials were not provided'),
            403: OpenApiResponse(description='Permission denied - Not an Admin or Manager'),
            404: OpenApiResponse(description='Card not found'),
        },
        examples=[
            OpenApiExample(
                'Approve Application',
                summary='Approve a card application',
                value={'status': 'APPROVED'},
                request_only=True,
            ),
            OpenApiExample(
                'Reject Application',
                summary='Reject a card application with reason',
                value={
                    'status': 'REJECTED',
                    'rejection_reason': 'Insufficient credit score'
                },
                request_only=True,
            ),
        ]
    )
    def post(self, request, pk):
        try:
            credit_card = self.get_object(pk)
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            if credit_card.status != 'PENDING':
                return Response(
                    {
                        'error': 'Only pending applications can be updated',
                        'current_status': credit_card.status
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Update card status
            credit_card.status = serializer.validated_data['status']

            # Set additional fields based on status
            if credit_card.status == 'APPROVED':
                credit_card.approved_by = request.user
                credit_card.rejection_reason = None  # Clear any existing rejection reason
            elif credit_card.status == 'REJECTED':
                credit_card.approved_by = None  # Clear any existing approver
                credit_card.rejection_reason = serializer.validated_data.get('rejection_reason')

            credit_card.save()

            # Log the action
            action = 'approved' if credit_card.status == 'APPROVED' else 'rejected'

            return Response({
                'message': f'Card successfully {action}',
                'data': CreditCardDetailSerializer(credit_card).data
            }, status=status.HTTP_200_OK)

        except Http404:
            return Response(
                {'error': 'Card not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception:
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
