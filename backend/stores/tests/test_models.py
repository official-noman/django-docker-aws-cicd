"""
Tests for store/tenant models and subscription logic.
"""

import pytest
from datetime import timedelta
from django.utils import timezone

from stores.models import Store, Subscription, StoreUser, StoreRole, SubscriptionPlan


@pytest.mark.django_db
class TestStoreModel:
    def test_create_store(self):
        store = Store.objects.create(name="Test Store", slug="test-store")
        assert str(store) == "Test Store"
        assert store.is_active is True

    def test_slug_uniqueness(self):
        Store.objects.create(name="A", slug="unique-slug")
        with pytest.raises(Exception):
            Store.objects.create(name="B", slug="unique-slug")


@pytest.mark.django_db
class TestSubscriptionModel:
    def test_trial_auto_sets_end_date(self, store):
        sub = Subscription.objects.create(store=store)
        assert sub.trial_end_date is not None
        assert sub.plan == SubscriptionPlan.TRIAL

    def test_trial_days_remaining(self, store):
        sub = Subscription.objects.create(store=store)
        assert sub.days_remaining is not None
        assert sub.days_remaining <= 14

    def test_trial_expired(self, store):
        sub = Subscription.objects.create(
            store=store,
            trial_start_date=timezone.now() - timedelta(days=30),
            trial_end_date=timezone.now() - timedelta(days=16),
        )
        assert sub.is_trial_expired is True

    def test_paid_plan_not_trial_expired(self, store):
        sub = Subscription.objects.create(store=store, plan=SubscriptionPlan.PRO)
        assert sub.is_trial_expired is False
        assert sub.days_remaining is None


@pytest.mark.django_db
class TestStoreUserModel:
    def test_owner_role(self, owner_membership):
        assert owner_membership.is_owner is True
        assert owner_membership.role == StoreRole.OWNER

    def test_staff_role(self, staff_membership):
        assert staff_membership.is_owner is False
        assert staff_membership.role == StoreRole.STAFF

    def test_unique_together(self, user, store, owner_membership):
        with pytest.raises(Exception):
            StoreUser.objects.create(
                user=user, store=store, role=StoreRole.STAFF
            )
