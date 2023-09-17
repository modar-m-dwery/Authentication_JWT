from django.contrib.auth import get_user_model, update_session_auth_hash
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from .models import UserProfile
from .permissions import IsOwnerOrReadOnly
from .serializers import (ChangePasswordSerializer, UserLoginSerializer,
                          UserProfileSerializer, UserRegistrationSerializer)

User = get_user_model()


# Registration
class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        user_type = user.get_user_type_display()
        message = f"User '{user.name}' registered as a {user_type}."
        return Response(
            {"message": message, "user_type": user.user_type},
            status=status.HTTP_201_CREATED,
        )


# login
class CustomTokenObtainPairView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserLoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        access = AccessToken.for_user(user)

        return Response(
            {
                "message": "Login successful.",
                "refresh": str(refresh),
                "access": str(access),
                "user_type": user.user_type,
            },
            status=status.HTTP_200_OK,
        )


# logout
class UserLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh_token")
        print(refresh_token)

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response(
                    {"detail": "User logged out successfully."},
                    status=status.HTTP_200_OK,
                )
            except Exception:
                return Response(
                    {"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"detail": "Refresh token not provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )


# change password
class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data.get("old_password")
            new_password = serializer.validated_data.get("new_password")

            # Check if the old password is correct
            if not user.check_password(old_password):
                return Response(
                    {"detail": "Old password is incorrect."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Set the new password and update the session auth hash
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)

            return Response(
                {"detail": "Password changed successfully."},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# profile
class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsOwnerOrReadOnly, permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return UserProfile.objects.all()
        else:
            return UserProfile.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        try:
            user_profile = self.get_object()
            super().perform_update(serializer)
            new_name = serializer.validated_data.get("name")
            if new_name is not None:
                user_profile.user.name = new_name
                user_profile.user.save()

            print("UserProfile updated successfully")
        except Exception as e:
            print("Error updating UserProfile:", str(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        # Add the user's name from the related CustomUser
        data = serializer.data
        data["name"] = instance.user.name
        return Response(data)
