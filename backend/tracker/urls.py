from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ReadingViewSet, RegisterView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Setup DRF router for users and readings
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'readings', ReadingViewSet, basename='readings')

urlpatterns = [
    path('v1/', include([
        # 📦 Resource endpoints
        path('', include(router.urls)),

        # 🔐 Auth endpoints
        path('auth/register/', RegisterView.as_view(), name='register'),

        # 🔑 JWT authentication endpoints
        path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    ])),
]
