from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import Menu, Booking

class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ['id', 'title', 'price', 'inventory']

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'name', 'no_of_guests', 'booking_date', 'owner']
        read_only_fields = ['owner']

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'password']
        read_only_fields = ['id']
    def validate(self, attrs):
        user = get_user_model()(username=attrs.get('username'), email=attrs.get('email', ''))
        try:
            validate_password(attrs['password'], user)
        except ValidationError as error:
            raise serializers.ValidationError({'password': error.messages})
        return attrs
    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)
