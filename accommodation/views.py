from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.cache import never_cache, cache_control
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from decimal import Decimal
from .models import Accommodation, Booking, Student, Room
from .forms import AccommodationImageForm
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import smtplib
from datetime import date
import json

# ✅ Custom discount library
from studentaccommodationpkg.festival_discount import FestivalDiscountLib

# ✅ AWS integrations
from .sns_utils import send_sns_notification
from .sqs_utils import send_booking_message


# 🩺 ✅ Health check endpoint for Elastic Beanstalk
@csrf_exempt
def health_check(request):
    """AWS Elastic Beanstalk health check endpoint."""
    return HttpResponse("OK", status=200)


# ✅ AWS Lambda test API
@csrf_exempt
def check_room_api(request):
    api_gateway_url = "https://31amd0e7lj.execute-api.us-east-1.amazonaws.com/prod/checkroom"
    payload = {"room_id": 101, "is_available": True, "discount": 15}
    try:
        response = requests.post(api_gateway_url, json=payload)
        response.raise_for_status()
        return JsonResponse(response.json())
    except requests.exceptions.RequestException as e:
        print("❌ Lambda error:", e)
        return JsonResponse({"error": "Failed to connect"}, status=500)


# 🏘️ Room list view
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
@login_required(login_url='login')
def room_list(request):
    rooms = Room.objects.select_related('accommodation', 'accommodation__festival_discount')
    discounted_rooms = []
    booked_room_ids = Booking.objects.values_list('room_id', flat=True)

    for room in rooms:
        acc = room.accommodation
        original_price = Decimal(acc.price_per_month)
        final_price = original_price
        discount_percent = Decimal(0)
        festival_name = None

        if acc.festival_discount and acc.festival_discount.is_active():
            # ✅ Fixed logic
            festival = FestivalDiscountLib()
            discount_percent = acc.festival_discount.percentage
            final_price = festival.apply_discount(original_price, discount_percent)
            festival_name = acc.festival_discount.name

        status = "Booked" if room.id in booked_room_ids else "Available"

        discounted_rooms.append({
            "room": room,
            "status": status,
            "original_price": original_price,
            "final_price": final_price,
            "discount_percent": discount_percent,
            "festival_name": festival_name,
        })

    return render(request, 'accommodation/room_list.html', {'discounted_rooms': discounted_rooms})


# 🏡 Accommodation detail view
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
@login_required(login_url='login')
def accommodation_detail(request, pk):
    accommodation = get_object_or_404(Accommodation, pk=pk)
    rooms = Room.objects.filter(accommodation=accommodation)
    original_price = accommodation.price_per_month
    discount_percent = Decimal(0)
    final_price = original_price
    festival_name = None

    if accommodation.festival_discount and accommodation.festival_discount.is_active():
        # ✅ Fixed logic
        festival = FestivalDiscountLib()
        discount_percent = accommodation.festival_discount.percentage
        final_price = festival.apply_discount(original_price, discount_percent)
        festival_name = accommodation.festival_discount.name

    booked_rooms = Booking.objects.values_list('room_id', flat=True)
    has_available_rooms = Room.objects.filter(accommodation=accommodation, status="Available").exists()

    return render(request, 'accommodation/accommodation_detail.html', {
        'accommodation': accommodation,
        'rooms': rooms,
        'original_price': original_price,
        'final_price': round(final_price, 2),
        'discount_percent': discount_percent,
        'festival_name': festival_name,
        'booked_rooms': booked_rooms,
        'has_available_rooms': has_available_rooms,
    })


# ✅ Booking View (SQS + SNS + Email)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
@login_required(login_url='login')
def book_room(request, pk):
    accommodation = get_object_or_404(Accommodation, pk=pk)
    available_room = Room.objects.filter(accommodation=accommodation, status="Available").first()

    if not available_room:
        messages.error(request, "❌ No available rooms for this accommodation.")
        return redirect("accommodation:accommodation_detail", pk=pk)

    student, _ = Student.objects.get_or_create(user=request.user)

    booking = Booking.objects.create(
        student=student,
        room=available_room,
        original_price=accommodation.price_per_month,
        discount_applied=accommodation.get_discount_amount(),
        final_price=accommodation.get_final_price(),
    )

    available_room.status = "Booked"
    available_room.save()

    # ✅ Step 1: Send booking info to SQS
    try:
        send_booking_message(booking)
        print("✅ Booking data sent to SQS successfully!")
    except Exception as e:
        print("❌ Failed to send message to SQS:", e)

    # ✅ Step 2: Send admin SNS alert
    try:
        subject = f"📢 New Booking: {accommodation.title}"
        message = (
            f"New Booking Alert!\n\n"
            f"Accommodation: {accommodation.title}\n"
            f"Room: {available_room.room_number}\n"
            f"Booked By: {request.user.username}\n"
            f"Final Price: €{booking.final_price:.2f}\n"
            f"Date: {booking.date_booked.strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        send_sns_notification(subject, message)
    except Exception as e:
        print("❌ SNS notification failed:", e)

    # ✅ Step 3: Email confirmation to user
    try:
        sender_email = "kharish820414@gmail.com"
        receiver_email = request.user.email
        password = "krpyvsrdkkodwpju"

        subject = "🎉 Booking Confirmed - Student Accommodation"
        body = f"""
        <html>
          <body style="font-family: 'Poppins', Arial, sans-serif;">
            <h3 style="color:#198754;">Booking Confirmed!</h3>
            <p>Hi {request.user.username},</p>
            <p>Your booking for <b>{accommodation.title}</b> has been confirmed.</p>
            <p><b>Room:</b> {available_room.room_number}<br>
            <b>Final Price:</b> €{booking.final_price:.2f}</p>
            <p>Thank you for choosing Student Accommodation!</p>
          </body>
        </html>
        """

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("✅ Booking confirmation email sent successfully!")

    except Exception as e:
        print("❌ Email send failed:", e)

    return render(request, "accommodation/booking_confirmation.html", {
        "booking": booking,
        "accommodation": accommodation,
        "room": available_room,
    })


# 📘 My Bookings View
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
@login_required(login_url='login')
def my_bookings(request):
    student = Student.objects.filter(user=request.user).first()
    bookings = Booking.objects.filter(student=student).select_related('room', 'room__accommodation')

    if request.method == "POST":
        booking_id = request.POST.get("booking_id")
        booking = Booking.objects.filter(id=booking_id, student=student).first()
        if booking:
            booking.room.status = "Available"
            booking.room.save()
            booking.delete()
            return redirect("accommodation:my_bookings")

    return render(request, "accommodation/my_bookings.html", {"bookings": bookings})


# 👤 Register View
@never_cache
def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not email or not password1 or not password2:
            messages.error(request, "⚠️ All fields are required.")
            return redirect('accommodation:register')

        if password1 != password2:
            messages.error(request, "❌ Passwords do not match.")
            return redirect('accommodation:register')

        if User.objects.filter(username=email).exists():
            messages.error(request, "⚠️ Email already registered. Please log in.")
            return redirect('login')

        user = User.objects.create_user(username=email, email=email, password=password1)
        user.save()
        messages.success(request, "🎉 Account created successfully! You can now log in.")
        return redirect('login')

    return render(request, 'registration/register.html')


# 🖼️ Upload Accommodation Image
@login_required(login_url='login')
def upload_accommodation_image(request, pk):
    accommodation = get_object_or_404(Accommodation, pk=pk)

    if request.method == 'POST':
        form = AccommodationImageForm(request.POST, request.FILES, instance=accommodation)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Accommodation image updated successfully!")
            return redirect('accommodation:accommodation_detail', pk=pk)
        else:
            messages.error(request, "❌ Failed to upload image. Please try again.")
    else:
        form = AccommodationImageForm(instance=accommodation)

    return render(request, 'accommodation/upload_accommodation_image.html', {
        'form': form,
        'accommodation': accommodation
    })
