from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import DataViewSet

router = DefaultRouter()
router.register(r'Data', DataViewSet, basename='data')


urlpatterns = [
    path('', include(router.urls)),
]
