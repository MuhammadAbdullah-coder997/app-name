from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ReadingViewSet, RegisterView

# DRF router for users and readings
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'readings', ReadingViewSet, basename='readings')

urlpatterns = [
    path('api/v1/', include([
        path('', include(router.urls)),  # ViewSet routes
        path('auth/register/', RegisterView.as_view(), name='register'),  # User registration
    ])),
]
