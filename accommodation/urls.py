from django.urls import path
from . import views

app_name = 'accommodation'

urlpatterns = [
    # 🩺 Health check endpoint (for AWS Elastic Beanstalk)
    path('health/', views.health_check, name='health_check'),

    # 🏘️ Room list (Home Page)
    path('', views.room_list, name='accommodation_list'),

    # 🏡 Accommodation detail
    path('<int:pk>/', views.accommodation_detail, name='accommodation_detail'),

    # ⚡ Instant Booking
    path('<int:pk>/book-room/', views.book_room, name='book_room'),

    # 📘 My bookings
    path('my-bookings/', views.my_bookings, name='my_bookings'),

    # 👤 Register page
    path('register/', views.register, name='register'),

    # 🖼️ Upload image for accommodation
    path('<int:pk>/upload-image/', views.upload_accommodation_image, name='upload_image'),
]
