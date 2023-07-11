from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import DataViewSet,TestViewSet,DeleteData

router = DefaultRouter()
router.register(r'Data', DataViewSet, basename='data')
router.register(r'Test', TestViewSet, basename='data')
router.register(r'Delete', TestViewSet, basename='data')
urlpatterns = [
    path('', include(router.urls)),
]
