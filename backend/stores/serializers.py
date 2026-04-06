from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.utils.text import slugify
from rest_framework import serializers

from .models import Store, Subscription, StoreUser, StoreRole


# ---------------------------------------------------------------------------
# Store Serializers
# ---------------------------------------------------------------------------
class SubscriptionSerializer(serializers.ModelSerializer):
    is_trial_expired = serializers.BooleanField(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    plan_display = serializers.CharField(source="get_plan_display", read_only=True)

    class Meta:
        model = Subscription
        fields = (
            "id",
            "plan",
            "plan_display",
            "trial_start_date",
            "trial_end_date",
            "is_active",
            "is_trial_expired",
            "days_remaining",
            "max_products",
            "max_staff",
        )
        read_only_fields = ("id", "trial_start_date", "trial_end_date")


class StoreSerializer(serializers.ModelSerializer):
    subscription = SubscriptionSerializer(read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = (
            "id",
            "name",
            "slug",
            "email",
            "phone",
            "address",
            "logo",
            "currency",
            "timezone",
            "is_active",
            "subscription",
            "member_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "slug", "created_at", "updated_at")

    def get_member_count(self, obj):
        return obj.members.filter(is_active=True).count()


class StoreCreateSerializer(serializers.ModelSerializer):
    """Used during onboarding — creates Store + Subscription + Owner membership."""

    class Meta:
        model = Store
        fields = ("name", "email", "phone", "address", "currency", "timezone")

    def create(self, validated_data):
        validated_data["slug"] = slugify(validated_data["name"])
        # Ensure unique slug
        base_slug = validated_data["slug"]
        counter = 1
        while Store.objects.filter(slug=validated_data["slug"]).exists():
            validated_data["slug"] = f"{base_slug}-{counter}"
            counter += 1

        store = Store.objects.create(**validated_data)

        # Auto-create trial subscription
        Subscription.objects.create(store=store)

        # Make the requesting user the owner
        user = self.context["request"].user
        StoreUser.objects.create(
            user=user,
            store=store,
            role=StoreRole.OWNER,
        )

        return store


# ---------------------------------------------------------------------------
# Store User / Member Serializers
# ---------------------------------------------------------------------------
class StoreUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = StoreUser
        fields = (
            "id",
            "username",
            "email",
            "role",
            "role_display",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class InviteStaffSerializer(serializers.Serializer):
    """Invite an existing user to the store as staff."""

    username = serializers.CharField()

    def validate_username(self, value):
        try:
            User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")
        return value

    def create(self, validated_data):
        user = User.objects.get(username=validated_data["username"])
        store = self.context["request"].store

        # Check staff limit
        sub = getattr(store, "subscription", None)
        if sub:
            current_staff = store.members.filter(is_active=True).count()
            if current_staff >= sub.max_staff:
                raise serializers.ValidationError(
                    f"Staff limit reached ({sub.max_staff}). Upgrade your plan."
                )

        membership, created = StoreUser.objects.get_or_create(
            user=user,
            store=store,
            defaults={"role": StoreRole.STAFF},
        )
        if not created and not membership.is_active:
            membership.is_active = True
            membership.save()

        return membership


# ---------------------------------------------------------------------------
# Registration (SaaS Onboarding)
# ---------------------------------------------------------------------------
class SaaSRegisterSerializer(serializers.Serializer):
    """
    All-in-one onboarding: creates User + Store + Subscription + Owner role.
    """

    # User fields
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True, validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True)

    # Store fields
    store_name = serializers.CharField(max_length=200)
    store_email = serializers.EmailField(required=False, default="")
    store_phone = serializers.CharField(max_length=20, required=False, default="")
    store_address = serializers.CharField(required=False, default="")
    currency = serializers.CharField(max_length=3, required=False, default="USD")

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        if User.objects.filter(username=attrs["username"]).exists():
            raise serializers.ValidationError(
                {"username": "This username is already taken."}
            )
        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError(
                {"email": "This email is already registered."}
            )
        return attrs

    def create(self, validated_data):
        # 1. Create User
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )

        # 2. Create Store
        slug = slugify(validated_data["store_name"])
        base_slug = slug
        counter = 1
        while Store.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        store = Store.objects.create(
            name=validated_data["store_name"],
            slug=slug,
            email=validated_data.get("store_email", ""),
            phone=validated_data.get("store_phone", ""),
            address=validated_data.get("store_address", ""),
            currency=validated_data.get("currency", "USD"),
        )

        # 3. Create Trial Subscription
        Subscription.objects.create(store=store)

        # 4. Assign Owner Role
        StoreUser.objects.create(
            user=user,
            store=store,
            role=StoreRole.OWNER,
        )

        return {"user": user, "store": store}
