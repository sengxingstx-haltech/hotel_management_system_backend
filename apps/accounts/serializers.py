from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        # fields = ('id', 'name', 'permissions')
        fields = '__all__'


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        # fields = ('id', 'name', 'codename')
        fields = '__all__'


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims to the payload (not the token itself)
        token['user_id'] = user.id
        token['email'] = user.email
        # ...

        return token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = ('id', 'username', 'email', 'first_name', 'last_name', 'groups')
        fields = '__all__'
        extra_kwargs = {
            'last_login': {'required': False},
            'date_joined': {'required': False},
            'password': {'write_only': True},
        }

    def validate_password(self, value):
        # Validate the new password using Django's password validation
        validate_password(value)
        return value

    def create(self, validated_data):
        # Hash the password before saving
        validated_data["password"] = make_password(validated_data["password"])

        # Set is_active to True
        validated_data['is_active'] = True

        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Remove password from validated_data to prevent updating it
        validated_data.pop('password', None)
        return super().update(instance, validated_data)

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')

        # If this is an update operation, remove the password field
        if self.instance:
            fields.pop('password')

        # If the user has the permission to modify the 'is_superuser' field
        # Otherwise, hide the 'is_superuser' field
        if request and request.method in ['POST', 'PUT', 'PATCH']:
            user = request.user

            if (
                not user.is_superuser
                and not user.groups.filter(permissions__codename='change_is_superuser').exists()
            ):
                fields.pop('is_staff')
                fields.pop('is_superuser')

        return fields


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ('email', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is not correct')
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        user = User.objects.filter(email=value).first()
        if user is None:
            raise serializers.ValidationError('User with this email does not exist')
        return value

    def save(self, **kwargs):
        user = User.objects.get(email=self.validated_data['email'])
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = f'http://your-frontend-url/reset-password-confirm/{uid}/{token}/'

        # Render email content
        subject = 'Password Reset'
        from_email = 'webmaster@example.com'
        to_email = user.email
        context = {
            'user': user,
            'reset_link': reset_link,
        }
        text_content = render_to_string('email/password_reset_email.txt', context)
        html_content = render_to_string('email/password_reset_email.html', context)

        # Send email
        email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        email.attach_alternative(html_content, 'text/html')
        email.send()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, attrs):
        try:
            uid = force_str(urlsafe_base64_decode(attrs['uid']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid token")

        if not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError("Invalid token or token expired")

        return attrs

    def save(self, **kwargs):
        uid = self.validated_data['uid']
        user = User.objects.get(pk=force_str(urlsafe_base64_decode(uid)))
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
