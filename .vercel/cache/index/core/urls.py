from django.urls import path
from . import views
from . import monitoring

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('events/', views.events, name='events'),
    path('pricing/', views.pricing, name='pricing'),
    path('private-lessons/', views.private_lessons, name='private_lessons'),
    path('resources/', views.resources_view, name='resources'),
    path('contact/', views.contact, name='contact'),
    path('contact/success/', views.contact_success, name='contact_success'),
    path('schedule/', views.schedule_view, name='schedule'),
    path('testimonials/', views.display_testimonials, name='testimonials'),
    path('testimonials/submit/', views.submit_testimonial, name='submit_testimonial'),
    path('testimonials/success/', views.testimonial_success, name='testimonial_success'),
    path('instructors/', views.instructor_list, name='instructors'),
    path('instructors/<int:instructor_id>/', views.instructor_detail, name='instructor_detail'),
    path('gallery/', views.gallery_view, name='gallery'),
    
    # Instagram integration endpoints
    path('webhooks/instagram/', views.instagram_webhook, name='instagram_webhook'),
    
    # Performance monitoring endpoints - SPEC_04 Group D
    path('sw.js', views.service_worker, name='service_worker'),
    path('offline/', views.offline_view, name='offline'),
    path('api/performance-metrics/', views.performance_metrics, name='performance_metrics'),
    path('api/performance-dashboard/', views.performance_dashboard_data, name='performance_dashboard_data'),
    
    # Booking system - SPEC_05 Group B Task 10
    path('booking/create/', views.create_booking, name='create_booking'),
    path('booking/success/<str:booking_id>/', views.booking_success, name='booking_success'),
    
    # Email testing - SPEC_05 Group B Task 10
    path('email-test/', views.email_test, name='email_test'),
    
    # Calendly integration test - SPEC_05 Group A
    path('calendly-test/', views.calendly_test, name='calendly_test'),
    
    # Pastio.fun RSVP integration - SPEC_05 Group B Task 7
    path('api/rsvp/submit/', views.submit_rsvp, name='submit_rsvp'),
    path('api/rsvp/counts/', views.get_rsvp_counts, name='get_rsvp_counts'),
    
    # Database performance monitoring - SPEC_06 Group B Task 6
    # path('admin/db-performance-stats/', views.db_performance_stats, name='db_performance_stats'),
    # path('admin/clear-cache/', views.clear_cache, name='clear_cache'),
    
    # Health check for CI/CD deployments - SPEC_06 Group D Task 10
    path('api/health/', views.health_check, name='health_check'),
    
    # Comprehensive Monitoring and Health Check Endpoints - SPEC_06 Group C Task 9
    path('health/', monitoring.health_check, name='monitoring_health_check'),
    path('health/simple/', monitoring.health_check_simple, name='health_check_simple'),
    path('uptime/', monitoring.uptime_status, name='uptime_status'),
    path('api/metrics/', monitoring.metrics_endpoint, name='metrics_endpoint'),
    path('api/monitoring/status/', monitoring.monitoring_status, name='monitoring_status'),
    
    # Admin Monitoring Dashboard - SPEC_06 Group C Task 9
    path('admin/monitoring/', monitoring.monitoring_dashboard, name='monitoring_dashboard'),
    path('admin/monitoring/clear-cache/', monitoring.clear_monitoring_cache, name='clear_monitoring_cache'),
    path('admin/monitoring/test-alerts/', monitoring.test_alerts, name='test_alerts'),
] 