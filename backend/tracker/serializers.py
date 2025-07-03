from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, Reading
import re


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with validation for personal information.
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'age', 'weight', 'height', 'has_diabetes', 'has_hypertension',
            'date_joined'
        ]
        read_only_fields = ['id', 'date_joined', 'full_name']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate_email(self, value):
        """Validate email format and uniqueness."""
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', value):
            raise serializers.ValidationError("Invalid email format")
        if User.objects.filter(email=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate_age(self, value):
        """Validate age is within realistic range."""
        if value is not None and (value < 0 or value > 150):
            raise serializers.ValidationError("Age must be between 0 and 150")
        return value

    def validate_weight(self, value):
        """Validate weight is within realistic range."""
        if value is not None and (value < 20 or value > 500):
            raise serializers.ValidationError("Weight must be between 20 and 500 kg")
        return value

    def validate_height(self, value):
        """Validate height is within realistic range."""
        if value is not None and (value < 50 or value > 250):
            raise serializers.ValidationError("Height must be between 50 and 250 cm")
        return value

    def validate(self, data):
        """Cross-field validation."""
        if data.get('has_diabetes') and data.get('age') is not None and data.get('age') < 10:
            raise serializers.ValidationError({
                "has_diabetes": "Diabetes diagnosis unlikely for age under 10"
            })
        return data


class ReadingSerializer(serializers.ModelSerializer):
    """
    Serializer for Reading model with calculated fields and validation.
    """
    blood_pressure_category = serializers.SerializerMethodField()
    glucose_mmol = serializers.SerializerMethodField()
    glucose_mg = serializers.SerializerMethodField()

    class Meta:
        model = Reading
        fields = [
            'id', 'user', 'systolic', 'diastolic', 'glucose_level',
            'glucose_unit', 'notes', 'created_at', 'updated_at',
            'blood_pressure_category', 'glucose_mmol', 'glucose_mg'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at',
            'blood_pressure_category', 'glucose_mmol', 'glucose_mg'
        ]
        extra_kwargs = {
            'user': {'required': True},
            'systolic': {'required': True},
            'diastolic': {'required': True},
            'glucose_level': {'required': False},
        }

    def validate_systolic(self, value):
        if value < 50 or value > 300:
            raise serializers.ValidationError("Systolic pressure must be between 50 and 300 mmHg")
        return value

    def validate_diastolic(self, value):
        if value < 30 or value > 200:
            raise serializers.ValidationError("Diastolic pressure must be between 30 and 200 mmHg")
        return value

    def validate_glucose_level(self, value):
        if value is not None:
            if value <= 0:
                raise serializers.ValidationError("Glucose level must be positive")
            unit = self.initial_data.get('glucose_unit', 'mg/dL')
            if unit == 'mmol/L' and value > 50:
                raise serializers.ValidationError("Glucose level in mmol/L seems too high")
            elif unit == 'mg/dL' and value > 900:
                raise serializers.ValidationError("Glucose level in mg/dL seems too high")
        return value

    def validate(self, data):
        if 'systolic' in data and 'diastolic' in data:
            if data['systolic'] <= data['diastolic']:
                raise serializers.ValidationError({
                    "systolic": "Systolic pressure must be higher than diastolic"
                })
        return data

    def get_blood_pressure_category(self, obj):
        if obj.systolic is None or obj.diastolic is None:
            return None
        return obj.get_blood_pressure_category()

    def get_glucose_mmol(self, obj):
        if obj.glucose_level is None:
            return None
        return obj.get_glucose_in_mmol_l()

    def get_glucose_mg(self, obj):
        if obj.glucose_level is None:
            return None
        return obj.get_glucose_in_mg_dl()

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new user.
    Validates user input, ensures password confirmation, and creates a user with hashed password.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = (
            'email', 'first_name', 'last_name', 'password', 'password2',
            'age', 'weight', 'height', 'has_diabetes', 'has_hypertension'
        )
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'age': {'required': False},
            'weight': {'required': False},
            'height': {'required': False},
            'has_diabetes': {'required': False, 'default': False},
            'has_hypertension': {'required': False, 'default': False}
        }

    def validate_email(self, value):
        """Validate email format and uniqueness."""
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', value):
            raise serializers.ValidationError("Please enter a valid email address.")
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value.lower()

    def validate_age(self, value):
        """Validate age is within a realistic range."""
        if value is not None:
            if not isinstance(value, int) or value < 0 or value > 150:
                raise serializers.ValidationError("Age must be between 0 and 150 years.")
        return value

    def validate_weight(self, value):
        """Validate weight is within a realistic range."""
        if value is not None:
            if not isinstance(value, (int, float)) or value < 20 or value > 500:
                raise serializers.ValidationError("Weight must be between 20 and 500 kg.")
        return value

    def validate_height(self, value):
        """Validate height is within a realistic range."""
        if value is not None:
            if not isinstance(value, (int, float)) or value < 50 or value > 250:
                raise serializers.ValidationError("Height must be between 50 and 250 cm.")
        return value

    def validate_password(self, value):
        """Enhance password validation with custom error messages."""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(
                f"Password is invalid: {', '.join(str(msg) for msg in e.messages)}"
            )
        return value

    def validate(self, data):
        """Validate that passwords match and perform cross-field checks."""
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        
        # Cross-field validation for health conditions
        if data.get('has_diabetes') and data.get('age') is not None and data['age'] < 10:
            raise serializers.ValidationError(
                {"has_diabetes": "Diabetes diagnosis is unlikely for age under 10."}
            )
        if data.get('has_hypertension') and data.get('age') is not None and data['age'] < 10:
            raise serializers.ValidationError(
                {"has_hypertension": "Hypertension diagnosis is unlikely for age under 10."}
            )
        return data

    def create(self, validated_data):
        """Create a new user with hashed password and return serialized data."""
        validated_data.pop('password2')  # Remove confirmation password
        try:
            user = User.objects.create_user(
                email=validated_data['email'],
                password=validated_data['password'],
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', ''),
                age=validated_data.get('age'),
                weight=validated_data.get('weight'),
                height=validated_data.get('height'),
                has_diabetes=validated_data.get('has_diabetes', False),
                has_hypertension=validated_data.get('has_hypertension', False)
            )
            # Return serialized user data for consistent API response
            return user
        except Exception as e:
            raise serializers.ValidationError(f"Failed to create user: {str(e)}")

    def to_representation(self, instance):
        """Customize the response to exclude sensitive fields."""
        from .serializers import UserSerializer  # Avoid circular import
        serializer = UserSerializer(instance)
        return serializer.data