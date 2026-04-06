"""
Shared test fixtures for the multi-tenant SaaS project.
"""

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from stores.models import Store, Subscription, StoreUser, StoreRole
from inventory.models import Category, Product


# ---------------------------------------------------------------------------
# Auth Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def api_client():
    """Unauthenticated DRF test client."""
    return APIClient()


@pytest.fixture
def user(db):
    """Standard test user."""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123!",
    )


@pytest.fixture
def admin_user(db):
    """Django superuser."""
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass123!",
    )


@pytest.fixture
def staff_user(db):
    """A separate user to be assigned as staff."""
    return User.objects.create_user(
        username="staffuser",
        email="staff@example.com",
        password="staffpass123!",
    )


# ---------------------------------------------------------------------------
# Store / Tenant Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def store(db):
    """A sample store / tenant."""
    return Store.objects.create(
        name="Test Shop",
        slug="test-shop",
        email="shop@example.com",
        currency="USD",
    )


@pytest.fixture
def store_subscription(store):
    """Trial subscription for the store."""
    return Subscription.objects.create(store=store)


@pytest.fixture
def another_store(db):
    """Second store — used for data isolation tests."""
    s = Store.objects.create(
        name="Other Shop",
        slug="other-shop",
        email="other@example.com",
    )
    Subscription.objects.create(store=s)
    return s


# ---------------------------------------------------------------------------
# Store Membership Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def owner_membership(user, store, store_subscription):
    """User is the owner of the store."""
    return StoreUser.objects.create(
        user=user,
        store=store,
        role=StoreRole.OWNER,
    )


@pytest.fixture
def staff_membership(staff_user, store, store_subscription):
    """Staff user attached to the store."""
    return StoreUser.objects.create(
        user=staff_user,
        store=store,
        role=StoreRole.STAFF,
    )


# ---------------------------------------------------------------------------
# Authenticated Clients
# ---------------------------------------------------------------------------
@pytest.fixture
def owner_client(user, owner_membership, store):
    """APIClient authenticated as the store owner, with X-Store-ID header."""
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}",
        HTTP_X_STORE_ID=str(store.id),
    )
    return client


@pytest.fixture
def staff_client(staff_user, staff_membership, store):
    """APIClient authenticated as staff, with X-Store-ID header."""
    client = APIClient()
    refresh = RefreshToken.for_user(staff_user)
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}",
        HTTP_X_STORE_ID=str(store.id),
    )
    return client


@pytest.fixture
def other_store_client(another_store):
    """Authenticated client for a DIFFERENT store — tests data isolation."""
    other_user = User.objects.create_user(
        username="otherowner",
        email="otherowner@example.com",
        password="otherpass123!",
    )
    StoreUser.objects.create(
        user=other_user,
        store=another_store,
        role=StoreRole.OWNER,
    )
    client = APIClient()
    refresh = RefreshToken.for_user(other_user)
    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}",
        HTTP_X_STORE_ID=str(another_store.id),
    )
    return client


# ---------------------------------------------------------------------------
# Inventory Data Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def category(store):
    """Sample category belonging to the test store."""
    return Category.objects.create(
        store=store,
        name="Electronics",
        description="Electronic devices and gadgets",
    )


@pytest.fixture
def another_category(store):
    """Second sample category."""
    return Category.objects.create(
        store=store,
        name="Furniture",
        description="Home and office furniture",
    )


@pytest.fixture
def product(store, category):
    """Sample product — normal stock level."""
    return Product.objects.create(
        store=store,
        name="Wireless Mouse",
        sku="ELEC-001",
        barcode="1234567890123",
        description="Ergonomic wireless mouse",
        cost_price=15.00,
        selling_price=29.99,
        quantity=150,
        low_stock_threshold=10,
        category=category,
        is_active=True,
    )


@pytest.fixture
def low_stock_product(store, category):
    """Product at low stock level."""
    return Product.objects.create(
        store=store,
        name="USB Cable",
        sku="ELEC-002",
        barcode="1234567890456",
        description="USB-C to USB-A cable",
        cost_price=3.00,
        selling_price=9.99,
        quantity=3,
        low_stock_threshold=10,
        category=category,
        is_active=True,
    )


@pytest.fixture
def out_of_stock_product(store, category):
    """Product with zero stock."""
    return Product.objects.create(
        store=store,
        name="HDMI Adapter",
        sku="ELEC-003",
        description="HDMI to DisplayPort adapter",
        cost_price=5.00,
        selling_price=14.99,
        quantity=0,
        low_stock_threshold=5,
        category=category,
        is_active=True,
    )


@pytest.fixture
def other_store_product(another_store):
    """Product in a DIFFERENT store — should never be visible to test store."""
    cat = Category.objects.create(
        store=another_store, name="Other Category"
    )
    return Product.objects.create(
        store=another_store,
        name="Invisible Product",
        sku="OTHER-001",
        cost_price=5.00,
        selling_price=10.00,
        quantity=99,
        category=cat,
    )
