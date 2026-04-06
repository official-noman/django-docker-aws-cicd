"""
Serializer validation tests — multi-tenant.
"""

import pytest
from unittest.mock import MagicMock

from inventory.serializers import ProductCreateUpdateSerializer, CategorySerializer
from stores.serializers import SaaSRegisterSerializer


@pytest.mark.django_db
class TestProductCreateUpdateSerializer:
    def _make_request(self, store):
        req = MagicMock()
        req.store = store
        return req

    def test_valid_data(self, store, category):
        data = {
            "name": "Test Product",
            "sku": "TEST-001",
            "cost_price": 10.00,
            "selling_price": 19.99,
            "quantity": 50,
            "category": str(category.id),
        }
        serializer = ProductCreateUpdateSerializer(
            data=data, context={"request": self._make_request(store)}
        )
        assert serializer.is_valid(), serializer.errors

    def test_negative_selling_price_rejected(self, store):
        data = {
            "name": "Bad Price",
            "sku": "BAD-001",
            "cost_price": 5.00,
            "selling_price": -5.00,
            "quantity": 10,
        }
        serializer = ProductCreateUpdateSerializer(
            data=data, context={"request": self._make_request(store)}
        )
        assert not serializer.is_valid()
        assert "selling_price" in serializer.errors

    def test_negative_quantity_rejected(self, store):
        data = {
            "name": "Bad Qty",
            "sku": "BAD-002",
            "cost_price": 5.00,
            "selling_price": 10.00,
            "quantity": -1,
        }
        serializer = ProductCreateUpdateSerializer(
            data=data, context={"request": self._make_request(store)}
        )
        assert not serializer.is_valid()
        assert "quantity" in serializer.errors

    def test_zero_selling_price_rejected(self, store):
        data = {
            "name": "Free Item",
            "sku": "FREE-001",
            "cost_price": 0,
            "selling_price": 0,
            "quantity": 10,
        }
        serializer = ProductCreateUpdateSerializer(
            data=data, context={"request": self._make_request(store)}
        )
        assert not serializer.is_valid()
        assert "selling_price" in serializer.errors

    def test_cross_store_category_rejected(self, store, another_store):
        """Cannot assign a category from another store."""
        from inventory.models import Category as Cat

        other_cat = Cat.objects.create(store=another_store, name="Alien Category")
        data = {
            "name": "Cross Store",
            "sku": "CROSS-001",
            "cost_price": 5.00,
            "selling_price": 10.00,
            "quantity": 5,
            "category": str(other_cat.id),
        }
        serializer = ProductCreateUpdateSerializer(
            data=data, context={"request": self._make_request(store)}
        )
        assert not serializer.is_valid()
        assert "category" in serializer.errors


@pytest.mark.django_db
class TestCategorySerializer:
    def test_valid_data(self):
        data = {"name": "Clothing", "description": "All types of clothing"}
        serializer = CategorySerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_name_required(self):
        serializer = CategorySerializer(data={"description": "Missing name"})
        assert not serializer.is_valid()
        assert "name" in serializer.errors


@pytest.mark.django_db
class TestSaaSRegisterSerializer:
    def test_valid_registration(self):
        data = {
            "username": "newshopowner",
            "email": "newshop@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
            "store_name": "My New Shop",
        }
        serializer = SaaSRegisterSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_password_mismatch(self):
        data = {
            "username": "newshopowner",
            "email": "newshop@example.com",
            "password": "StrongPass123!",
            "password_confirm": "WrongPass!",
            "store_name": "My New Shop",
        }
        serializer = SaaSRegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "password_confirm" in serializer.errors

    def test_duplicate_username(self, user):
        data = {
            "username": "testuser",  # already exists in fixture
            "email": "unique@example.com",
            "password": "StrongPass123!",
            "password_confirm": "StrongPass123!",
            "store_name": "Dup Shop",
        }
        serializer = SaaSRegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "username" in serializer.errors
