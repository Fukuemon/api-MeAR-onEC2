from rest_framework import viewsets
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
)
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from ..profiles.serializers import ProfileSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser, AllowAny


def staff_required(view_func):
    """
    スタッフ権限が必要なエンドポイントに付与するデコレーター
    :param view_func:
    :return:
    """

    def wrapped_view(view_instance, request, *args, **kwargs):
        if request.user_staff:
            return view_func(view_instance, request, *args, **kwargs)
        else:
            return Response({"message": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

    return wrapped_view




class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        return self.get_serializer().Meta.model.objects.filter(is_active=True)

    def get_object(self):
        return get_object_or_404(self.get_queryset(), pk=self.kwargs.get('pk'))

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return [IsAdminUser()]

    def list(self, request):
        user_serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(user_serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        user_serializer = UserCreateSerializer(data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response(user_serializer.data, status=status.HTTP_201_CREATED)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, partial=False):
        user = self.get_object()
        user_serializer = self.serializer_class(user, data=request.data, partial=partial)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response({"message": "User updated successfully", "data": user_serializer.data}, status=status.HTTP_200_OK)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({"message": "User deleted successfully"}, status=status.HTTP_200_OK)



class MyAccountViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request):
        user = self.get_object()
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request):
        user = self.get_object()
        serializer = self.serializer_class(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Account updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"], detail=False)
    def change_password(self, request):
        user = self.get_object()
        password_serializer = ChangePasswordSerializer(data=request.data, context={"user": user})
        if password_serializer.is_valid():
            user.set_password(password_serializer.validated_data["password1"])
            user.save()
            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
        else:
            return Response(password_serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request,*args, **keywargs):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(username=email, password=password)


        if user:
            login_serializer = self.serializer_class(data=request.data)
            if login_serializer.is_valid():
                profile = user.profile
                return Response({
                    "access": login_serializer.validated_data.get("access"),
                    "refresh": login_serializer.validated_data.get("refresh"),
                    "profile": ProfileSerializer(profile).data,
                    "message": "ログイン成功"
                }, status=status.HTTP_200_OK)
            else:
                return Response(login_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "ユーザーが存在しません"}, status=status.HTTP_404_NOT_FOUND)

