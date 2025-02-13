from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser, MultiPartParser
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from .models import CreditCard
from .serializers import (
    CreditCardApplicationSerializer,
    CreditCardDetailSerializer,
    CardStatusUpdateSerializer
)
from .permissions import IsAdminOrManager, IsAdminOrManagerOrOwner


class CreditCardListCreateView(APIView):
    """
    Handles listing all credit cards for Admins/Managers
    and creating a new credit card application.
    """
    permission_classes = [IsAuthenticated, IsAdminOrManagerOrOwner]
    parser_classes = (MultiPartParser, JSONParser,)
    @extend_schema(
        tags=['Credit Cards'],
        summary='List all credit cards',
        description='List all credit cards (Admin/Manager) or only user\'s cards',
        responses={
            200: CreditCardDetailSerializer(many=True),
            401: OpenApiResponse(description='Authentication credentials were not provided'),
            403: OpenApiResponse(description='Permission denied - Not an Admin or Manager'),
        },
        examples=[
            OpenApiExample(
                'Credit Cards',
                summary='List all credit cards',
                value={},
                request_only=True,
            ),
        ]
    )
    def get(self, request):
        """ List all credit cards (Admin/Manager) or only user's cards """
        user = request.user
        queryset = CreditCard.objects.all() if user.role in ['ADMIN', 'MANAGER'] else CreditCard.objects.filter(user=user)
        serializer = CreditCardDetailSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Credit Cards'],
        summary='Submit a new credit card application',
        description='Submit a new credit card application',
        request=CreditCardApplicationSerializer,
        responses={
            201: CreditCardDetailSerializer,
            400: OpenApiResponse(description='Bad request - Invalid data'),
            401: OpenApiResponse(description='Authentication credentials were not provided'),
            403: OpenApiResponse(description='Permission denied - Not an Admin or Manager'),
            500: OpenApiResponse(description='Server error - An unexpected error occurred'),
        },
        examples=[
            OpenApiExample(
                'Credit Card Application',
                summary='Submit a new credit card application',
                value={
                    'card_type': 'VISA',
                    'credit_limit': 5000
                },
                request_only=True,
        )]
    )
    def post(self, request):
        """ Submit a new credit card application """
        serializer = CreditCardApplicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            credit_card = CreditCard(
                user=request.user,
                card_type=serializer.validated_data.get('card_type', 'VISA'),
                credit_limit=serializer.validated_data.get('credit_limit'),
                status='PENDING'
            )
            credit_card.save()

            return Response(CreditCardDetailSerializer(credit_card).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreditCardDetailView(APIView):
    """
    Handles retrieving, updating, and deleting a specific credit card.
    """
    permission_classes = [IsAuthenticated, IsAdminOrManagerOrOwner]
    parser_classes = (JSONParser, MultiPartParser,)
    @extend_schema(
        tags=['Credit Cards'],
        summary='Retrieve credit card details',
        description='Retrieve credit card details',
        responses={
            200: CreditCardDetailSerializer,
            401: OpenApiResponse(description='Authentication credentials were not provided'),
            403: OpenApiResponse(description='Permission denied - Not an Admin or Manager'),
            404: OpenApiResponse(description='Card not found'),
        },
        examples=[
            OpenApiExample(
                'Credit Card Details',
                summary='Retrieve credit card details',
                value={},
                request_only=True,
            ),
        ]
    )
    def get_object(self, pk, user):
        """ Fetch card instance or raise 404 """
        try:
            if user.role in ['ADMIN', 'MANAGER']:
                return CreditCard.objects.get(pk=pk)
            return CreditCard.objects.get(pk=pk, user=user)
        except CreditCard.DoesNotExist:
            raise Http404

    @extend_schema(
        tags=['Credit Cards'],
        summary='Retrieve credit card details by ID',
        description='Retrieve credit card details (Admin/Manager) or user\'s card',
        responses={
            200: CreditCardDetailSerializer,
            401: OpenApiResponse(description='Authentication credentials were not provided'),
            403: OpenApiResponse(description='Permission denied - Not an Admin or Manager'),
            404: OpenApiResponse(description='Card not found'),
        }
    )
    def get(self, request, pk):
        """ Retrieve credit card details """
        try:
            if request.user.role in ['ADMIN', 'MANAGER']:
                credit_card = self.get_object(pk, request.user)
                serializer = CreditCardDetailSerializer(credit_card)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                credit_card = self.get_object(pk, request.user)
                serializer = CreditCardDetailSerializer(credit_card)
                return Response(serializer.data, status=status.HTTP_200_OK)

        except Http404:
            return Response({'error': 'Card not found'}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        tags=['Credit Cards'],
        summary='Delete credit card application',
        description='Delete credit card application (Admin only)',
        request=CreditCardApplicationSerializer,
        responses={
            200: CreditCardDetailSerializer,
            400: OpenApiResponse(description='Bad request - Invalid data'),
            401: OpenApiResponse(description='Authentication credentials were not provided'),
            403: OpenApiResponse(description='Permission denied - Not an Admin or Manager'),
            404: OpenApiResponse(description='Card not found'),
            500: OpenApiResponse(description='Server error - An unexpected error occurred'),
        },
        examples=[
            OpenApiExample(
                'Credit Card Application',
                summary='Delete credit card application',
                value={
                    'card_type': 'VISA',
                    'credit_limit': 5000
                },
                request_only=True,
            ),
        ]
    )
    def delete(self, request, pk):
        """ Delete a credit card application (Admin only) """
        if request.user.role != 'ADMIN':
            return Response({'error': 'Only admin can delete applications'}, status=status.HTTP_403_FORBIDDEN)

        credit_card = self.get_object(pk, request.user)
        credit_card.delete()
        return Response({'message': 'Card deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class CreditCardStatusUpdateView(APIView):
    """
    Handles updating the status of a credit card application.
    (Admin/Manager only)
    """
    permission_classes = [IsAdminOrManager]
    parser_classes = (JSONParser, MultiPartParser,)

    def get_object(self, pk):
        """ Fetch credit card instance or raise 404 """
        try:
            return CreditCard.objects.get(pk=pk)
        except CreditCard.DoesNotExist:
            raise Http404

    @extend_schema(
        tags=['Credit Cards'],
        summary='Update credit card application status',
        description='Update credit card application status (Admin/Manager only)',
        request=CardStatusUpdateSerializer,
        responses={
            200: CreditCardDetailSerializer,
            400: OpenApiResponse(description='Bad request - Invalid data or card not in pending status'),
            403: OpenApiResponse(description='Permission denied - Not an Admin or Manager'),
            404: OpenApiResponse(description='Card not found'),
        },
        examples=[
            OpenApiExample('Approve Application', summary='Approve a card application', value={'status': 'APPROVED'}, request_only=True),
            OpenApiExample('Reject Application', summary='Reject a card application with reason', value={'status': 'REJECTED', 'rejection_reason': 'Low credit score'}, request_only=True),
        ]
    )
    def post(self, request, pk):
        """ Update credit card status (Admin/Manager Only) """
        credit_card = self.get_object(pk)
        serializer = CardStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # if credit_card.status != 'PENDING':
        #     return Response({'error': 'Only pending applications can be updated', 'current_status': credit_card.status},
        #                     status=status.HTTP_400_BAD_REQUEST)

        credit_card.status = serializer.validated_data['status']

        if credit_card.status == 'APPROVED':
            credit_card.approved_by = request.user
            credit_card.rejection_reason = None
        elif credit_card.status == 'REJECTED':
            credit_card.approved_by = None
            credit_card.rejection_reason = serializer.validated_data.get('rejection_reason')

        credit_card.save()

        action = 'approved' if credit_card.status == 'APPROVED' else 'rejected'
        return Response({'message': f'Card successfully {action}', 'data': CreditCardDetailSerializer(credit_card).data},
                        status=status.HTTP_200_OK)

class CreditCardLimitUpdateView(APIView):
    """
    Handles updating the credit limit of an approved credit card.
    (Admin/Manager only)
    """
    permission_classes = [IsAdminOrManager]
    parser_classes = (JSONParser, MultiPartParser,)

    def get_object(self, pk):
        """ Fetch credit card instance or raise 404 """
        try:
            return CreditCard.objects.get(pk=pk)
        except CreditCard.DoesNotExist:
            raise Http404

    @extend_schema(
        tags=['Credit Cards'],
        summary='Update credit limit of an approved credit card',
        description='Update credit limit of an approved credit card (Admin/Manager only)',
        request=CardStatusUpdateSerializer,
        responses={
            200: CreditCardDetailSerializer,
            400: OpenApiResponse(description='Bad request - Invalid data or card not approved'),
            403: OpenApiResponse(description='Permission denied - Not an Admin or Manager'),
            404: OpenApiResponse(description='Card not found'),
        },
        examples=[
            OpenApiExample('Increase Credit Limit', summary='Update credit limit', value={'credit_limit': 10000}, request_only=True),
        ]
    )
    def patch(self, request, pk):
        """ Update credit card limit (Admin/Manager Only) """
        credit_card = self.get_object(pk)
        new_credit_limit = request.data.get('credit_limit')

        if not isinstance(new_credit_limit, (int, float)) or new_credit_limit <= 0:
            return Response({'error': 'Invalid credit limit value'}, status=status.HTTP_400_BAD_REQUEST)

        if credit_card.status != 'APPROVED':
            return Response({'error': 'Only approved cards can have their limit changed', 'current_status': credit_card.status},
                            status=status.HTTP_400_BAD_REQUEST)

        credit_card.credit_limit = new_credit_limit
        credit_card.save()

        return Response({'message': 'Credit limit updated successfully', 'data': CreditCardDetailSerializer(credit_card).data},
                        status=status.HTTP_200_OK)


