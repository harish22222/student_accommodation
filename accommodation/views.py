from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.cache import never_cache, cache_control
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from decimal import Decimal
from .models import Accommodation, Booking, Student, Room
from .sqs_utils import send_booking_message
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests


# ✅ AWS Lambda integration example
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


# 🏘️ Room list view (requires login)
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
@login_required(login_url='login')
def room_list(request):
    rooms = Room.objects.select_related('accommodation', 'accommodation__festival_discount')
    discounted_rooms = []
    booked_room_ids = Booking.objects.values_list('room_id', flat=True)

    for room in rooms:
        acc = room.accommodation
        original_price = acc.price_per_month
        discount_percent = 0
        final_price = original_price

        if acc.festival_discount and acc.festival_discount.is_active():
            discount_percent = acc.festival_discount.percentage
            final_price = original_price - (original_price * discount_percent / 100)

        status = "Booked" if room.id in booked_room_ids else "Available"

        discounted_rooms.append({
            "room": room,
            "status": status,
            "original_price": original_price,
            "final_price": round(final_price, 2),
            "discount_percent": discount_percent,
            "festival_name": acc.festival_discount.name if acc.festival_discount else None
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

    discount_percent = 0
    final_price = original_price
    festival_name = None

    if accommodation.festival_discount and accommodation.festival_discount.is_active():
        discount_percent = accommodation.festival_discount.percentage
        festival_name = accommodation.festival_discount.name
        final_price = original_price - (original_price * discount_percent / 100)

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


# ✅ Instant Booking View
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

    # ✅ Send SQS message
    try:
        send_booking_message(booking)
        print("✅ SQS booking message sent successfully!")
    except Exception as e:
        print("❌ SQS send failed:", e)

    # ✅ Send email confirmation
    sender_email = "kharish820414@gmail.com"
    receiver_email = request.user.email
    password = "krpyvsrdkkodwpju"

    subject = "🎉 Booking Confirmation"
    body = f"""
    <html>
      <body style="font-family: 'Poppins', Arial, sans-serif; background-color: #f4f6f8; padding: 40px;">
        <div style="max-width:600px; margin:auto; background:white; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.1); overflow:hidden;">
          <div style="background-color:#198754; color:white; text-align:center; padding:20px;">
            <h2 style="margin:0;">Booking Confirmed!</h2>
          </div>
          <div style="padding:25px 30px;">
            <p style="font-size:16px;">Hi <strong>{request.user.username}</strong>,</p>
            <p style="font-size:16px;">
              Your booking for <strong style="color:#0d6efd;">{accommodation.title}</strong> is confirmed.
            </p>
            <hr style="margin:20px 0; border:none; border-top:1px solid #ddd;">
            <p style="font-size:15px;"><strong>Room:</strong> {available_room.room_number}</p>
            <p style="font-size:15px;"><strong>Original Price:</strong> €{booking.original_price:.2f}</p>
            <p style="font-size:15px;"><strong>Discount Applied:</strong> €{booking.discount_applied:.2f}</p>
            <p style="font-size:15px;"><strong>Final Price:</strong> €{booking.final_price:.2f}</p>
            <hr style="margin:20px 0; border:none; border-top:1px solid #ddd;">
            <p style="text-align:center; font-size:14px; color:#666;">
              Thank you for booking with <strong>Student Accommodation</strong>!<br>
              We look forward to welcoming you.
            </p>
          </div>
        </div>
      </body>
    </html>
    """

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("✅ Booking email sent successfully!")
    except Exception as e:
        print("❌ Email send failed:", e)

    messages.success(request, f"🎉 Room {available_room.room_number} booked successfully!")
    return redirect("accommodation:my_bookings")


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


# 👤 Register View (public)
@never_cache
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "🎉 Account created successfully! You can now log in.")
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
