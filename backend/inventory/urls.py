from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, GlobalProductViewSet, StoreProductViewSet

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"global-catalog", GlobalProductViewSet, basename="globalproduct")
router.register(r"products", StoreProductViewSet, basename="storeproduct")

urlpatterns = [
    path("", include(router.urls)),
]