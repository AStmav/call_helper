from django.contrib import admin
from .models import TimeSlot, BookingSession, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'telegram_id') 
    search_fields = ('user__username', 'telegram_username')
    list_filter = ('telegram_id',)


@admin.register(BookingSession)
class BookingSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner_session', 'public_link', 'created_at')
    search_fields = ('title', 'public_link')
    list_filter = ('created_at', 'owner_session')


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('owner', 'start_time', 'end_time', 'is_booked', 'booked_by', 'session')
    list_filter = ('is_booked', 'start_time', 'owner')
    search_fields = ('owner__username', 'guest_name')
    date_hierarchy = 'start_time'