"""
API endpoint integration tests — multi-tenant SaaS.
"""

import pytest
from django.urls import reverse
from rest_framework import status


# ═══════════════════════════════════════════════════════════════════════════
# AUTH & ONBOARDING
# ═══════════════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestSaaSOnboarding:
    def test_register_creates_user_store_and_subscription(self, api_client):
        url = reverse("auth-register")
        response = api_client.post(url, {
            "username": "shopowner1",
            "email": "shop1@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
            "store_name": "My Corner Shop",
            "currency": "BDT",
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"] is True
        assert "tokens" in response.data["data"]
        assert response.data["data"]["store"]["name"] == "My Corner Shop"

    def test_obtain_token(self, api_client, user):
        url = reverse("token-obtain-pair")
        response = api_client.post(url, {
            "username": "testuser",
            "password": "testpass123!",
        })
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_profile_with_store_memberships(self, owner_client):
        url = reverse("auth-me")
        response = owner_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["user"]["username"] == "testuser"
        assert response.data["data"]["active_store"] is not None


# ═══════════════════════════════════════════════════════════════════════════
# DATA ISOLATION
# ═══════════════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestDataIsolation:
    def test_cannot_see_other_store_products(
        self, owner_client, product, other_store_product
    ):
        """Owner should only see products from their own store."""
        url = reverse("product-list")
        response = owner_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        skus = [p["sku"] for p in response.data["results"]]
        assert "ELEC-001" in skus
        assert "OTHER-001" not in skus

    def test_cannot_see_other_store_categories(
        self, owner_client, category, another_store
    ):
        from inventory.models import Category

        Category.objects.create(store=another_store, name="Secret Category")
        url = reverse("category-list")
        response = owner_client.get(url)
        names = [c["name"] for c in response.data["results"]]
        assert "Electronics" in names
        assert "Secret Category" not in names

    def test_other_store_client_cannot_see_my_products(
        self, other_store_client, product
    ):
        url = reverse("product-list")
        response = other_store_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0


# ═══════════════════════════════════════════════════════════════════════════
# ROLE-BASED ACCESS
# ═══════════════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestRoleBasedAccess:
    def test_owner_can_create_product(self, owner_client, category):
        url = reverse("product-list")
        data = {
            "name": "Keyboard",
            "sku": "ELEC-100",
            "cost_price": 30.00,
            "selling_price": 59.99,
            "quantity": 25,
            "category": str(category.id),
        }
        response = owner_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_staff_cannot_create_product(self, staff_client, category):
        url = reverse("product-list")
        data = {
            "name": "Staff Product",
            "sku": "STAFF-001",
            "cost_price": 5.00,
            "selling_price": 10.00,
            "quantity": 5,
            "category": str(category.id),
        }
        response = staff_client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_staff_can_read_products(self, staff_client, product):
        url = reverse("product-list")
        response = staff_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_staff_can_update_quantity(self, staff_client, product):
        url = reverse("product-detail", kwargs={"pk": product.pk})
        response = staff_client.patch(url, {"quantity": 200})
        assert response.status_code == status.HTTP_200_OK

    def test_staff_cannot_update_price(self, staff_client, product):
        url = reverse("product-detail", kwargs={"pk": product.pk})
        response = staff_client.patch(url, {"selling_price": 99.99})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_staff_cannot_delete_product(self, staff_client, product):
        url = reverse("product-detail", kwargs={"pk": product.pk})
        response = staff_client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_access_denied(self, api_client):
        url = reverse("product-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ═══════════════════════════════════════════════════════════════════════════
# PRODUCT CRUD (Owner)
# ═══════════════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestProductAPI:
    def test_list_products(self, owner_client, product):
        url = reverse("product-list")
        response = owner_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_retrieve_product(self, owner_client, product):
        url = reverse("product-detail", kwargs={"pk": product.pk})
        response = owner_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["sku"] == "ELEC-001"
        assert "profit_margin" in response.data

    def test_update_product(self, owner_client, product):
        url = reverse("product-detail", kwargs={"pk": product.pk})
        response = owner_client.patch(url, {"selling_price": 34.99})
        assert response.status_code == status.HTTP_200_OK

    def test_delete_product(self, owner_client, product):
        url = reverse("product-detail", kwargs={"pk": product.pk})
        response = owner_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_search_products(self, owner_client, product):
        url = reverse("product-list")
        response = owner_client.get(url, {"search": "Wireless"})
        assert response.data["count"] == 1

    def test_barcode_scan(self, owner_client, product):
        url = reverse("product-scan", kwargs={"barcode": "1234567890123"})
        response = owner_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["sku"] == "ELEC-001"

    def test_barcode_scan_not_found(self, owner_client):
        url = reverse("product-scan", kwargs={"barcode": "0000000000000"})
        response = owner_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_low_stock_endpoint(self, owner_client, low_stock_product):
        url = reverse("product-low-stock")
        response = owner_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_create_invalid_price(self, owner_client, category):
        url = reverse("product-list")
        data = {
            "name": "Bad Product",
            "sku": "BAD-001",
            "cost_price": 5.00,
            "selling_price": -10,
            "quantity": 5,
            "category": str(category.id),
        }
        response = owner_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ═══════════════════════════════════════════════════════════════════════════
# CATEGORY CRUD
# ═══════════════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestCategoryAPI:
    def test_list_categories(self, owner_client, category):
        url = reverse("category-list")
        response = owner_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_create_category(self, owner_client):
        url = reverse("category-list")
        response = owner_client.post(url, {
            "name": "Office Supplies",
            "description": "Pens, paper, and more",
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["slug"] == "office-supplies"

    def test_staff_cannot_create_category(self, staff_client):
        url = reverse("category-list")
        response = staff_client.post(url, {"name": "Forbidden"})
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ═══════════════════════════════════════════════════════════════════════════
# SYSTEM & DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════
@pytest.mark.django_db
class TestSystemEndpoints:
    def test_health_check_public(self, api_client):
        url = reverse("health-check")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "healthy"
        assert response.data["version"] == "2.0.0"

    def test_dashboard_stats(self, owner_client, product, low_stock_product):
        url = reverse("dashboard-stats")
        response = owner_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        data = response.data["data"]
        assert data["total_products"] == 2
        assert "potential_profit" in data
        assert "subscription" in data

    def test_dashboard_unauthenticated(self, api_client):
        url = reverse("dashboard-stats")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
