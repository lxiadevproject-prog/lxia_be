from django.contrib.auth import authenticate
from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from .models import UserProfile, Role


class UserProfileSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['role', 'role_display', 'phone', 'institution', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    groups = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'groups', 'profile']
        read_only_fields = ['id', 'is_active']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError('Credenciales inválidas. Verifica tu usuario y contraseña.')

        if not user.is_active:
            raise serializers.ValidationError('Esta cuenta de usuario ha sido desactivada.')

        attrs['user'] = user
        return attrs

    def create_or_get_token(self):
        user = self.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return user, token.key


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=8)
    confirm_password = serializers.CharField(required=True, write_only=True, min_length=8)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Las nuevas contraseñas no coinciden.'})
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('La contraseña actual no es correcta.')
        return value

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UserCreateSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=Role.choices, default=Role.CONTENT_MANAGER, write_only=True)
    phone = serializers.CharField(required=False, allow_blank=True, write_only=True)
    institution = serializers.CharField(required=False, allow_blank=True, write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password', 'role', 'phone', 'institution']

    def create(self, validated_data):
        role = validated_data.pop('role', Role.CONTENT_MANAGER)
        phone = validated_data.pop('phone', None)
        institution = validated_data.pop('institution', None)
        password = validated_data.pop('password')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=password
        )

        UserProfile.objects.create(
            user=user,
            role=role,
            phone=phone,
            institution=institution
        )

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=Role.choices, required=False)
    phone = serializers.CharField(required=False, allow_blank=True)
    institution = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'is_active', 'role', 'phone', 'institution']

    def update(self, instance, validated_data):
        role = validated_data.pop('role', None)
        phone = validated_data.pop('phone', None)
        institution = validated_data.pop('institution', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        profile, _ = UserProfile.objects.get_or_create(user=instance)
        if role is not None:
            profile.role = role
        if phone is not None:
            profile.phone = phone
        if institution is not None:
            profile.institution = institution
        profile.save()

        return instance
