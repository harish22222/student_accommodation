from django.urls import path
from . import views

app_name = 'accommodation'

urlpatterns = [
    # 🏘️ Room list
    path('', views.room_list, name='accommodation_list'),

    # 🏡 Accommodation detail
    path('<int:pk>/', views.accommodation_detail, name='accommodation_detail'),

    # ⚡ Instant Booking
    path('<int:pk>/book-room/', views.book_room, name='book_room'),

    # 📘 My bookings
    path('my-bookings/', views.my_bookings, name='my_bookings'),

    # 👤 Register page (kept here for now)
    path('register/', views.register, name='register'),
    
    path('<int:pk>/upload-image/', views.upload_accommodation_image, name='upload_image'),

]
