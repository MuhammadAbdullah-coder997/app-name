from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ReadingViewSet, RegisterView, LoginView, LogoutView

# DRF router for users and readings
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'readings', ReadingViewSet, basename='readings')

urlpatterns = [
    path('v1/', include([
        path('', include(router.urls)),  # ViewSet routes
        path('auth/register/', RegisterView.as_view(), name='register'),  # User registration
        path('auth/login/', LoginView.as_view(), name='login'),
        path('auth/logout/', LogoutView.as_view(), name='logout'),
    ])),
]
