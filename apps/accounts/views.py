from rest_framework import viewsets
from .serializers import (
    UserSerializer,
    UserCreateSerializer
)
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from .serializers import ChangePasswordSerializer

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
        if self.queryset is None:
            self.queryset = self.get_serializer().Meta.model.objects.filter(is_active=True)
            return self.queryset
        else:
            return self.queryset

    def get_object(self, pk):
        return get_object_or_404(self.get_queryset(), pk=pk)

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        else:
            return super().get_permissions()

    def list(self, request):
        user_serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(user_serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        user_serializer = UserCreateSerializer(data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response(user_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        user = self.get_object(pk=pk)
        user_serializer = self.serializer_class(user, data=request.data)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response({"message": "User updated successfully", "data": user_serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staff_required
    def destroy(self, request, pk=None):
        user = self.get_object(pk=pk)
        user.is_active = False
        if user.is_active == False:
            user.save()
            return Response({"message": "User deleted successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "User not deleted"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"], detail=True)
    def change_password(self, request, pk=None):
        user = self.get_object(pk=pk)
        password_serializer = ChangePasswordSerializer(data=request.data, context={"user": user})
        if password_serializer.is_valid():
            user.set_password(password_serializer.validated_data.get("password1"))
            user.save()
            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
        else:
            return Response(password_serializer.errors, status=status.HTTP_400_BAD_REQUEST)