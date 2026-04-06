"""
Unit tests for inventory models — multi-tenant.
"""

import pytest
from decimal import Decimal

from inventory.models import Category, Product


@pytest.mark.django_db
class TestCategoryModel:
    def test_create_category(self, store):
        cat = Category.objects.create(store=store, name="Books", description="All books")
        assert cat.name == "Books"
        assert cat.slug == "books"
        assert str(cat) == "Books"

    def test_slug_auto_generation(self, store):
        cat = Category.objects.create(store=store, name="Home & Garden")
        assert cat.slug == "home-garden"

    def test_product_count(self, category, product):
        assert category.product_count == 1

    def test_unique_slug_per_store(self, store):
        Category.objects.create(store=store, name="Food", slug="food")
        with pytest.raises(Exception):
            Category.objects.create(store=store, name="Food Dup", slug="food")


@pytest.mark.django_db
class TestProductModel:
    def test_create_product(self, product):
        assert product.name == "Wireless Mouse"
        assert product.sku == "ELEC-001"
        assert product.selling_price == Decimal("29.99")
        assert product.cost_price == Decimal("15.00")
        assert product.quantity == 150

    def test_str_representation(self, product):
        assert str(product) == "Wireless Mouse (ELEC-001)"

    def test_is_low_stock_false(self, product):
        assert product.is_low_stock is False

    def test_is_low_stock_true(self, low_stock_product):
        assert low_stock_product.is_low_stock is True

    def test_stock_value(self, product):
        expected = float(Decimal("15.00")) * 150
        assert product.stock_value == pytest.approx(expected, rel=1e-2)

    def test_retail_value(self, product):
        expected = float(Decimal("29.99")) * 150
        assert product.retail_value == pytest.approx(expected, rel=1e-2)

    def test_profit_margin(self, product):
        # margin = (29.99 - 15.00) / 29.99 * 100 ≈ 49.98%
        assert product.profit_margin == pytest.approx(49.98, abs=0.1)

    def test_unique_sku_per_store(self, product, store, category):
        with pytest.raises(Exception):
            Product.objects.create(
                store=store,
                name="Duplicate",
                sku="ELEC-001",
                cost_price=5.00,
                selling_price=10.00,
                quantity=5,
                category=category,
            )

    def test_same_sku_different_stores(self, product, another_store):
        """Different stores CAN have the same SKU."""
        p = Product.objects.create(
            store=another_store,
            name="Other Mouse",
            sku="ELEC-001",
            cost_price=10.00,
            selling_price=20.00,
            quantity=10,
        )
        assert p.sku == product.sku
        assert p.store != product.store

    def test_store_relationship(self, product, store):
        assert product.store == store
        assert product in store.products.all()
