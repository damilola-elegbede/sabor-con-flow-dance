from django.contrib import admin
from .models import Subscriber, Event, ClassRegistration

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subscribed_at', 'is_active')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('name', 'email')
    ordering = ('-subscribed_at',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'location', 'price', 'capacity', 'is_active')
    list_filter = ('is_active', 'date')
    search_fields = ('title', 'location')
    ordering = ('date', 'time')

@admin.register(ClassRegistration)
class ClassRegistrationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'event', 'registered_at', 'payment_status')
    list_filter = ('payment_status', 'registered_at', 'event')
    search_fields = ('name', 'email', 'phone')
    ordering = ('-registered_at',)
