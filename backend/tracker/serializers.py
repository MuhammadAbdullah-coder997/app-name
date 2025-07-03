from rest_framework import serializers
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
