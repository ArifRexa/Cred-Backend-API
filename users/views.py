from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
import requests
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.shortcuts import get_object_or_404

from cards.permissions import IsAdminOrManager
from users.tokens import account_activation_token
from .models import CustomUser
from .serializers import CustomUserSerializer, ResendActivationEmailSerializer, \
    PasswordResetSerializer, PasswordChangeSerializer, AuthSerializer, VerifyOTPSerializer, ResendOTPSerializer, \
    AccessTokenSerializer, UpdateUserSerializer, UserRoleUpdateSerializer, UserListSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (AllowAny,)


class VerifyOTPView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = VerifyOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'OTP verified'}, status=status.HTTP_200_OK)


class ResendOTPView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ResendOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = ResendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'New OTP sent'}, status=status.HTTP_200_OK)


class CustomTokenObtainPairView(TokenObtainPairView):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token


class UserInfoFromTokenAPI(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AuthSerializer

    @extend_schema(
        tags=['Profile'],
        summary = "Get authenticated user's profile",
        description = "Fetches the currently authenticated user's profile details from the access token.",
        responses = {
            200: OpenApiResponse(
                response=AuthSerializer,
                description="Successfully retrieved user information."
            ),
            401: OpenApiResponse(
                description="Unauthorized - Invalid or expired token."
            ),
            500: OpenApiResponse(
                description="Internal server error."
            )
        }

    )
    def get(self, request):
        # If authenticated, get the user from the request
        user = request.user
        user_data = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "dp": user.profile_picture.url if user.profile_picture else None,
            'role': user.role
        }
        return Response(user_data, status=status.HTTP_200_OK)


class UpdateUserInfoAPI(APIView):
    parser_classes = (JSONParser,)
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateUserSerializer

    @extend_schema(
        tags=['Profile'],
        summary='Update User Profile',
        description='Update user profile information. All fields are optional.',
        responses={
            200: UpdateUserSerializer,
            400: OpenApiResponse(description='Bad request'),
        },
    )
    def patch(self, request):
        user = request.user
        serializer = self.serializer_class(
            user,
            data=request.data,
            partial=True  # This allows partial updates
        )

        if serializer.is_valid():
            updated_user = serializer.save()
            # Return the updated data
            response_data = {
                'message': 'Profile updated successfully',
                'data': {
                    'first_name': updated_user.first_name,
                    'last_name': updated_user.last_name,
                    'profile_picture': request.build_absolute_uri(
                        updated_user.profile_picture.url) if updated_user.profile_picture else None
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        return Response(
            {
                'message': 'Invalid data provided',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class UpdateUserRoleView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = UserRoleUpdateSerializer

    @extend_schema(
        tags=['User Management'],
        summary='Update User Role',
        description='Update user role - Admin only endpoint',
        request=UserRoleUpdateSerializer,
        responses={
            200: OpenApiResponse(description='Role updated successfully'),
            400: OpenApiResponse(description='Invalid request'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='User not found')
        }
    )
    def patch(self, request, user_id):
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # Prevent admin from changing their own role
            if target_user == request.user:
                return Response(
                    {'error': 'Admin cannot change their own role'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Update user role
            target_user.role = serializer.validated_data['role']
            target_user.save()

            return Response({
                'message': 'User role updated successfully',
                'user_id': target_user.id,
                'email': target_user.email,
                'new_role': target_user.role
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserList(generics.ListAPIView):
    permission_classes = (IsAdminOrManager, )
    queryset = User.objects.all().order_by('pk')
    serializer_class = UserListSerializer
    page_size = 1

    @extend_schema(
        tags=['Profile'],
        summary = 'List of all users',
        description='Get a list of all users. Admin/Manager only.',
        responses = {
            200: UserListSerializer(many=True),
            401: OpenApiResponse(description='Authentication credentials were not provided'),
            403: OpenApiResponse(description='Permission denied - Not an Admin or Manager'),
        },
        examples=[
            OpenApiExample(
                'User List',
                summary='List of all users',
                value={},
                request_only=True,
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UserDetail(generics.RetrieveAPIView):
    permission_classes = (IsAdminOrManager, )
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @extend_schema(
        tags=['Profile'],
        summary='Get user details by ID',
        description='Get details of a specific user by ID. Admin/Manager.',
        responses={
            200: CustomUserSerializer,
            401: OpenApiResponse(description='Authentication credentials were not provided'),
            403: OpenApiResponse(description='Permission denied - Not an Admin'),
            404: OpenApiResponse(description='User not found'),
        }

    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'password reset email sent'}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = (AllowAny,)

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_object_or_404(User, pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            password = request.data.get('password')
            password_confirm = request.data.get('password_confirm')

            if password and password_confirm and password == password_confirm:
                user.set_password(password)
                user.save()
                return Response({'status': 'password reset complete'}, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'status': 'reset link is invalid'}, status=status.HTTP_400_BAD_REQUEST)
