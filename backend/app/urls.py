from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from inventory.views import HealthCheckView, DashboardStatisticsView
from stores.views import SaaSRegisterView, MyProfileView

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # ── Authentication ──────────────────────────────────────────────────
    path("api/auth/register/", SaaSRegisterView.as_view(), name="auth-register"),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("api/auth/me/", MyProfileView.as_view(), name="auth-me"),

    # ── API Documentation ───────────────────────────────────────────────
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    # ── System ──────────────────────────────────────────────────────────
    path("api/health/", HealthCheckView.as_view(), name="health-check"),
    path("api/dashboard/stats/", DashboardStatisticsView.as_view(), name="dashboard-stats"),

    # ── Store Management ────────────────────────────────────────────────
    path("api/store/", include("stores.urls")),

    # ── Inventory & POS APIs ──────────────────────────────────────────────
    path("api/inventory/", include("inventory.urls")),
    path("api/customers/", include("customers.urls")),
    path("api/orders/", include("orders.urls")),
]