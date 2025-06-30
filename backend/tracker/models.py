from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from typing import Any, Optional
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q

# -----------------------------
# Custom User Manager
# -----------------------------
class UserManager(BaseUserManager):
    def create_user(self, email: str, password: Optional[str] = None, **extra_fields: Any) -> 'User':
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: Optional[str] = None, **extra_fields: Any) -> 'User':
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

# -----------------------------
# Custom User Model
# -----------------------------
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("Email Address", unique=True)
    first_name = models.CharField("First Name", max_length=50, blank=True)
    last_name = models.CharField("Last Name", max_length=50, blank=True)
    age = models.PositiveIntegerField(
        "Age", null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(150)]
    )
    weight = models.FloatField(
        "Weight (kg)", null=True, blank=True,
        validators=[MinValueValidator(1.0), MaxValueValidator(500.0)]
    )
    height = models.FloatField(
        "Height (cm)", null=True, blank=True,
        validators=[MinValueValidator(30.0), MaxValueValidator(300.0)]
    )
    date_joined = models.DateTimeField("Date Joined", auto_now_add=True)
    is_active = models.BooleanField("Active", default=True)
    is_staff = models.BooleanField("Staff Status", default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    def __str__(self) -> str:
        return self.email

    def get_full_name(self) -> str:
        full = f"{self.first_name} {self.last_name}".strip()
        return full if full else self.email

    def get_short_name(self) -> str:
        return self.first_name or self.email

    def calculate_bmi(self) -> Optional[float]:
        if self.weight and self.height:
            height_m = self.height / 100
            return round(self.weight / (height_m ** 2), 2)
        return None

    class Meta:
        indexes = [
            models.Index(fields=['email'], name='email_idx'),
        ]
        permissions = [
            ("can_view_health_data", "Can view health-related data"),
        ]
        verbose_name = "User"
        verbose_name_plural = "Users"

# -----------------------------
# Reading Manager
# -----------------------------
class ReadingManager(models.Manager):
    def recent_readings(self, user, days=7):
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.filter(user=user, created_at__gte=cutoff)

    def abnormal_readings(self, user):
        return self.filter(
        Q(user=user) & (
            Q(systolic__gte=140) |
            Q(diastolic__gte=90) |
            Q(glucose_level__gte=200)
            )
        )


    # UPDATED METHOD
    def create_reading(self, user, systolic, diastolic, glucose_level, glucose_unit="mg/dL", notes=""):
        """
        Creates, validates, and saves a new Reading instance.
        This pattern ensures validation is run before saving.
        """
        reading = self.model(
            user=user,
            systolic=systolic,
            diastolic=diastolic,
            glucose_level=glucose_level,
            glucose_unit=glucose_unit,
            notes=notes
        )
        # Run model-level validation before committing to the database.
        reading.full_clean()
        reading.save(using=self._db)
        return reading

# -----------------------------
# Reading Model
# -----------------------------
class Reading(models.Model):
    GLUCOSE_UNITS = (
        ('mg/dL', 'mg/dL'),
        ('mmol/L', 'mmol/L'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='readings',
        help_text="User who recorded this reading"
    )
    systolic = models.PositiveIntegerField(
        help_text="Systolic blood pressure (e.g., 120)",
        validators=[MinValueValidator(50), MaxValueValidator(250)]
    )
    diastolic = models.PositiveIntegerField(
        help_text="Diastolic blood pressure (e.g., 80)",
        validators=[MinValueValidator(30), MaxValueValidator(150)]
    )
    glucose_level = models.FloatField(
        help_text="Blood glucose level",
        validators=[MinValueValidator(20.0), MaxValueValidator(600.0)]
    )
    glucose_unit = models.CharField(
        help_text="Unit of glucose measurement",
        max_length=10,
        choices=GLUCOSE_UNITS,
        default='mg/dL'
    )
    notes = models.TextField(
        help_text="Additional notes about the reading",
        blank=True
    )
    created_at = models.DateTimeField(
        help_text="Date and time when the reading was created",
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        help_text="Date and time when the reading was last updated",
        auto_now=True
    )

    objects = ReadingManager()

    def clean(self):
        # This validation runs when full_clean() is called.
        if self.systolic is not None and self.diastolic is not None:
            if self.systolic <= self.diastolic:
                raise ValidationError("Systolic blood pressure must be greater than diastolic blood pressure.")
        super().clean()

    def get_blood_pressure_category(self) -> str:
        if self.systolic is None or self.diastolic is None:
            return "Unknown"
        if self.systolic < 120 and self.diastolic < 80:
            return "Normal"
        elif 120 <= self.systolic <= 129 and self.diastolic < 80:
            return "Elevated"
        elif (130 <= self.systolic <= 139) or (80 <= self.diastolic <= 89):
            return "Hypertension Stage 1"
        elif self.systolic >= 140 or self.diastolic >= 90:
            return "Hypertension Stage 2"
        elif self.systolic > 180 or self.diastolic > 120:
            return "Hypertensive Crisis"
        return "Unknown"

    def get_glucose_in_mmol_l(self) -> float:
        if self.glucose_unit == 'mg/dL':
            return round(self.glucose_level / 18.0, 2)
        return self.glucose_level

    def get_glucose_in_mg_dl(self) -> float:
        if self.glucose_unit == 'mmol/L':
            return round(self.glucose_level * 18.0, 2)
        return self.glucose_level

    def __str__(self) -> str:
        time = self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else 'Unknown time'
        return f"{self.user.email}: BP {self.systolic}/{self.diastolic}, Glucose {self.glucose_level} {self.glucose_unit} on {time}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Health Reading"
        verbose_name_plural = "Health Readings"
        indexes = [
            models.Index(fields=['user'], name='reading_user_idx'),
            models.Index(fields=['created_at'], name='reading_recorded_idx'),
        ]
        permissions = [
            ("can_view_all_readings", "Can view all users' health readings"),
        ]