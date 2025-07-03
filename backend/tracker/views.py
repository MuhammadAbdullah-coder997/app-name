from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import User, Reading
from .serializers import UserSerializer, ReadingSerializer
from rest_framework.permissions import IsAuthenticated


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users (GET, POST, PATCH, DELETE).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own data
        return User.objects.filter(id=self.request.user.id)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()


class ReadingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for health readings (GET, POST, PATCH, DELETE).
    """
    serializer_class = ReadingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter readings only for the authenticated user
        return Reading.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='recent', url_name='recent_readings')
    def recent_readings(self, request):
        """
        Get recent readings for the past 7 days.
        """
        readings = Reading.objects.recent_readings(user=request.user)
        serializer = self.get_serializer(readings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='abnormal', url_name='abnormal_readings')
    def abnormal_readings(self, request):
        """
        Get abnormal readings (high blood pressure or glucose).
        """
        readings = Reading.objects.abnormal_readings(user=request.user)
        serializer = self.get_serializer(readings, many=True)
        return Response(serializer.data)
