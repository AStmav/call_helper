from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    path('slots/', views.my_slots, name='my_slots'),
    path('slots/create/', views.create_slot, name='create_slot'),
    path('slots/<int:slot_id>/delete/', views.delete_slot, name='delete_slot'),
    path('slots/<int:slot_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    
    path('sessions/', views.sessions_list, name='sessions_list'),
    path('sessions/create/', views.create_session, name='create_session'),
    path('sessions/<int:session_id>/edit/', views.edit_session, name='edit_session'),
    path('sessions/<int:session_id>/delete/', views.delete_session, name='delete_session'),
    
    path('public/<str:public_link>/', views.public_view, name='public_booking'),
    path('public/<str:public_link>/book/<int:slot_id>/', views.book_slot, name='book_slot'),
]