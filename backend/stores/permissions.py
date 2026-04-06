"""
Store-level permissions for role-based access control.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class HasStoreAccess(BasePermission):
    """
    Deny access if the user has no active store membership.
    """

    message = "You must belong to an active store to access this resource."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request, "store", None) is not None
        )


class IsStoreOwner(BasePermission):
    """
    Full access only for Store Owners.
    """

    message = "Only the store owner can perform this action."

    def has_permission(self, request, view):
        store_user = getattr(request, "store_user", None)
        if store_user is None:
            return False
        return store_user.is_owner


class IsStoreOwnerOrReadOnly(BasePermission):
    """
    Store Owners → full access.
    Staff → read-only access.
    """

    def has_permission(self, request, view):
        store_user = getattr(request, "store_user", None)
        if store_user is None:
            return False
        if request.method in SAFE_METHODS:
            return True
        return store_user.is_owner


class IsOwnerOrStockUpdate(BasePermission):
    """
    Store Owners → full CRUD.
    Staff → can only GET and PATCH (for stock/quantity updates).
    """

    def has_permission(self, request, view):
        store_user = getattr(request, "store_user", None)
        if store_user is None:
            return False

        if store_user.is_owner:
            return True

        # Staff can read and partially update (stock)
        if request.method in SAFE_METHODS:
            return True
        if request.method == "PATCH" and view.action == "partial_update":
            return True

        return False

    def has_object_permission(self, request, view, obj):
        store_user = getattr(request, "store_user", None)
        if store_user is None:
            return False

        if store_user.is_owner:
            return True

        # Staff can only update quantity-related fields
        if request.method == "PATCH":
            allowed_fields = {"quantity"}
            update_fields = set(request.data.keys())
            return update_fields.issubset(allowed_fields)

        return request.method in SAFE_METHODS


class SubscriptionIsActive(BasePermission):
    """
    Deny write operations if the store's subscription is inactive or trial expired.
    """

    message = "Your subscription is inactive or your trial has expired. Please upgrade."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        store = getattr(request, "store", None)
        if store is None:
            return False

        sub = getattr(store, "subscription", None)
        if sub is None:
            return False

        if not sub.is_active:
            return False
        if sub.is_trial_expired:
            return False

        return True
