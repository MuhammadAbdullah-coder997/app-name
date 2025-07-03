from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, ReadingViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'readings', ReadingViewSet, basename='reading')

urlpatterns = [
    path('', include(router.urls)),
]
