"""
Middleware that resolves the current Store context from the authenticated user.
Sets `request.store` and `request.store_user` on every request.
"""

from django.utils.functional import SimpleLazyObject

from stores.models import StoreUser


def _get_store_user(request):
    """Resolve the StoreUser for the current request."""
    if not hasattr(request, "_cached_store_user"):
        request._cached_store_user = None
        if request.user and request.user.is_authenticated:
            # Check for explicit store header (for multi-store users)
            store_id = request.headers.get("X-Store-ID")
            qs = StoreUser.objects.select_related("store", "store__subscription").filter(
                user=request.user, is_active=True, store__is_active=True
            )
            if store_id:
                request._cached_store_user = qs.filter(store_id=store_id).first()
            else:
                # Default to first active membership
                request._cached_store_user = qs.first()
    return request._cached_store_user


class StoreContextMiddleware:
    """
    Adds `request.store` and `request.store_user` to every request.

    For multi-store users, the client can pass the header:
        X-Store-ID: <uuid>
    to select which store context to use.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.store_user = SimpleLazyObject(lambda: _get_store_user(request))
        request.store = SimpleLazyObject(
            lambda: getattr(request.store_user, "store", None)
        )
        return self.get_response(request)
