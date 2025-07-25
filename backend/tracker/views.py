from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import AnonRateThrottle
from django.utils import timezone
from .models import User, Reading
from .serializers import UserSerializer, ReadingSerializer, RegisterSerializer
import logging

logger = logging.getLogger(__name__)

# -------------------------
# Custom Throttle for Register
# -------------------------
class RegisterThrottle(AnonRateThrottle):
    rate = '10/hour'  # Limit to 10 registrations per hour per IP

# -------------------------
# User Registration View
# -------------------------
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [RegisterThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            logger.info(f"User registered successfully: {user.email} (ID: {user.id})")
            response_serializer = UserSerializer(user)
            return Response(
                {
                    "message": "User registered successfully",
                    "user": response_serializer.data,
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Registration failed: {str(e)}")
            return Response(
                {"error": f"Registration failed: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

# -------------------------
# User ViewSet
# -------------------------
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()

# -------------------------
# Reading ViewSet
# -------------------------
class ReadingViewSet(viewsets.ModelViewSet):
    serializer_class = ReadingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Reading.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='recent', url_name='recent_readings')
    def recent_readings(self, request):
        readings = Reading.objects.recent_readings(user=request.user)
        serializer = self.get_serializer(readings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='abnormal', url_name='abnormal_readings')
    def abnormal_readings(self, request):
        readings = Reading.objects.abnormal_readings(user=request.user)
        serializer = self.get_serializer(readings, many=True)
        return Response(serializer.data)
