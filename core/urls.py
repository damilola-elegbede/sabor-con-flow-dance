from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('events/', views.events, name='events'),
    path('pricing/', views.pricing, name='pricing'),
    path('private-lessons/', views.private_lessons, name='private_lessons'),
    path('contact/', views.contact, name='contact'),
    path('contact/submit/', views.contact_submit, name='contact_submit'),
] 