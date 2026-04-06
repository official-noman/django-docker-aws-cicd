from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import StoreViewSet, StoreMemberViewSet

router = DefaultRouter()
router.register(r"members", StoreMemberViewSet, basename="store-member")

urlpatterns = [
    # GET  /api/store/          → current store details
    # PATCH /api/store/         → update store (owner only)
    path(
        "",
        StoreViewSet.as_view({"get": "list", "patch": "partial_update", "put": "update"}),
        name="store-detail",
    ),
    path("", include(router.urls)),
]
