import logging

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Store, StoreUser
from .permissions import HasStoreAccess, IsStoreOwner
from .serializers import (
    SaaSRegisterSerializer,
    StoreSerializer,
    StoreCreateSerializer,
    StoreUserSerializer,
    InviteStaffSerializer,
)

logger = logging.getLogger("stores")


# ---------------------------------------------------------------------------
# SaaS Onboarding
# ---------------------------------------------------------------------------
class SaaSRegisterView(APIView):
    """
    All-in-one registration: creates User + Store + Trial Subscription + Owner role.
    Returns JWT tokens so the user is immediately logged in.
    """

    permission_classes = [AllowAny]

    @extend_schema(request=SaaSRegisterSerializer, tags=["Auth"])
    def post(self, request):
        serializer = SaaSRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        user = result["user"]
        store = result["store"]

        # Issue JWT tokens
        refresh = RefreshToken.for_user(user)

        logger.info(
            "New SaaS registration: user=%s store=%s", user.username, store.name
        )

        return Response(
            {
                "success": True,
                "message": "Account created successfully. 14-day trial started.",
                "data": {
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                    "store": StoreSerializer(store).data,
                    "tokens": {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                    },
                },
            },
            status=status.HTTP_201_CREATED,
        )


# ---------------------------------------------------------------------------
# Store Management
# ---------------------------------------------------------------------------
@extend_schema_view(
    retrieve=extend_schema(tags=["Store"]),
    update=extend_schema(tags=["Store"]),
    partial_update=extend_schema(tags=["Store"]),
)
class StoreViewSet(viewsets.ModelViewSet):
    """
    Manage the current user's store.
    - Owners can update store details.
    - Staff can only read.
    """

    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated, HasStoreAccess]
    http_method_names = ["get", "patch", "put"]

    def get_queryset(self):
        return Store.objects.filter(
            id=self.request.store.id
        ).select_related("subscription")

    def get_object(self):
        return self.request.store

    @extend_schema(tags=["Store"])
    def list(self, request, *args, **kwargs):
        """Return the current store details."""
        store = self.get_object()
        serializer = self.get_serializer(store)
        return Response({"success": True, "data": serializer.data})


# ---------------------------------------------------------------------------
# Store Members
# ---------------------------------------------------------------------------
@extend_schema_view(
    list=extend_schema(tags=["Store Members"]),
    retrieve=extend_schema(tags=["Store Members"]),
    partial_update=extend_schema(tags=["Store Members"]),
    destroy=extend_schema(tags=["Store Members"]),
)
class StoreMemberViewSet(viewsets.ModelViewSet):
    """
    Manage store members (staff).
    Only Store Owners can invite, update roles, or remove members.
    """

    serializer_class = StoreUserSerializer
    permission_classes = [IsAuthenticated, HasStoreAccess, IsStoreOwner]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        return StoreUser.objects.filter(
            store=self.request.store
        ).select_related("user")

    @extend_schema(
        request=InviteStaffSerializer,
        responses={201: StoreUserSerializer},
        tags=["Store Members"],
    )
    def create(self, request, *args, **kwargs):
        """Invite a user to the store as staff."""
        serializer = InviteStaffSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        membership = serializer.save()
        logger.info(
            "Staff invited: %s → %s",
            membership.user.username,
            request.store.name,
        )
        return Response(
            {
                "success": True,
                "message": f"{membership.user.username} has been added to {request.store.name}.",
                "data": StoreUserSerializer(membership).data,
            },
            status=status.HTTP_201_CREATED,
        )

    def perform_destroy(self, instance):
        # Prevent owner from removing themselves
        if instance.is_owner:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("The store owner cannot be removed.")
        instance.is_active = False
        instance.save()
        logger.info("Member deactivated: %s", instance.user.username)


# ---------------------------------------------------------------------------
# My Profile (for any authenticated user)
# ---------------------------------------------------------------------------
class MyProfileView(APIView):
    """
    Returns the current user's profile with all store memberships.
    Optimized for mobile app session initialization.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["Auth"])
    def get(self, request):
        memberships = StoreUser.objects.filter(
            user=request.user, is_active=True
        ).select_related("store", "store__subscription")

        stores = []
        for m in memberships:
            stores.append(
                {
                    "store": StoreSerializer(m.store).data,
                    "role": m.role,
                    "role_display": m.get_role_display(),
                    "membership_id": str(m.id),
                }
            )

        return Response(
            {
                "success": True,
                "data": {
                    "user": {
                        "id": request.user.id,
                        "username": request.user.username,
                        "email": request.user.email,
                    },
                    "active_store": StoreSerializer(request.store).data
                    if request.store
                    else None,
                    "stores": stores,
                },
            }
        )
