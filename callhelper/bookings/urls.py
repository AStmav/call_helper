from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('slots/', views.my_slots, name='my_slots'),  # List of free slots
    path('slots/create/', views.create_slot, name='create_slot'),  # Creating slot
    path('public/<str:public_link>/', views.public_view, name='public_booking'),
]