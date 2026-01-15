from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid 

class BaseModel(models.Model):
    """
    An abstract base class model that provides self-updating
    'created_at' and 'updated_at' fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class BookingSession(BaseModel):
    """
    This model to save information about booking sessions
    """
    owner_session = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="booking_session",
    )
    title = models.CharField(
        max_length=60,    
    )
    description = models.TextField(
        blank=True,
        null=True,
    )
    public_link = models.CharField(
        max_length=100,
        unique=True
    )
    
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk:  # только при создании
            self.public_link = uuid.uuid4().hex[:12]
        super().save(*args, **kwargs)

class TimeSlot(BaseModel):
    """
    This model  to save  information about slots and bookings
    """
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="time_slots",
        help_text="Owner of slots , who take calling " 
    )
    session = models.ForeignKey(
        BookingSession,
        on_delete=models.CASCADE,
        related_name='session_slots',
        null=True,
        blank=True
    )
    start_time = models.DateTimeField(
        help_text="Start time of slot"
    )
    end_time = models.DateTimeField(
    )
    is_booked = models.BooleanField(
        default=False,
        help_text="Is this slot is booked"
    )
    booked_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="booked_slots",
        null=True,
        blank=True,
        help_text="Who booked this slot"
    )
    guest_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Guest name for booking without registration"
    )
    booked_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When it was booked"
    )
  
    def __str__(self):
        return f"{self.owner} | {self.start_time} - {self.end_time}"
    
    def get_duration(self):
        """Returns the duration of the slot as a timedelta"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
    
    def get_duration_display(self):
        """Returns a human-readable duration string"""
        duration = self.get_duration()
        if duration:
            total_seconds = int(duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            if hours > 0:
                return f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
            return f"{minutes}m"
        return "N/A"

        
    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError(
                "The end time must be later than the start time."
            )
        if self.is_booked and not self.booked_by and not self.guest_name:
            raise ValidationError(
                "Booked slot must have 'booked_by' or 'guest_name' specified."
            )
    
    def save(self, *args, **kwargs):
        # Синхронизация is_booked и booked_by
        if self.booked_by is not None or (self.guest_name and self.guest_name.strip()):
            self.is_booked = True
            if self.booked_at is None:  # Устанавливаем только если еще не установлен
                self.booked_at = timezone.now()
        else:
            self.is_booked = False
            self.booked_at = None  # Очищаем при отмене бронирования
        
        self.full_clean()
        super().save(*args, **kwargs)




