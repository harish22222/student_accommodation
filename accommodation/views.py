from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.cache import never_cache, cache_control
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from decimal import Decimal
from .models import Accommodation, Booking, Student, Room
from .sqs_utils import send_booking_message
from .sns_utils import send_sns_notification
from .forms import AccommodationImageForm
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


# ✅ Booking View → Confirmation Page Flow
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

    # ✅ Create booking entry
    booking = Booking.objects.create(
        student=student,
        room=available_room,
        original_price=accommodation.price_per_month,
        discount_applied=accommodation.get_discount_amount(),
        final_price=accommodation.get_final_price(),
    )

    # Update room status
    available_room.status = "Booked"
    available_room.save()

    # ✅ Send SQS message
    try:
        send_booking_message(booking)
        print("✅ SQS booking message sent successfully!")
    except Exception as e:
        print("❌ SQS send failed:", e)

    # ✅ Send SNS Notification (Admin)
    try:
        subject = "New Room Booking Notification"
        message = f"""
        New booking by {request.user.username} ({request.user.email})
        Accommodation: {accommodation.title}
        Room: {available_room.room_number}
        Final Price: €{booking.final_price:.2f}
        """
        send_sns_notification(subject, message)
        print("✅ SNS notification sent to admin successfully!")
    except Exception as e:
        print("❌ SNS Notification Failed:", e)

    # ✅ Send booking confirmation email to user
    try:
        sender_email = "kharish820414@gmail.com"
        receiver_email = request.user.email
        password = "krpyvsrdkkodwpju"

        subject = "🎉 Booking Confirmed - Student Accommodation"
        body = f"""
        <html>
          <body style="font-family: 'Poppins', Arial, sans-serif; background-color: #f4f6f8; padding: 40px; margin: 0;">
            <div style="max-width:600px; margin:auto; background:white; border-radius:12px; 
                        box-shadow:0 4px 15px rgba(0,0,0,0.1); overflow:hidden;">
              
              <!-- Header -->
              <div style="background-color:#198754; color:white; text-align:center; padding:20px 0;">
                <h2 style="margin:0; font-size:24px;">Booking Confirmed!</h2>
              </div>

              <!-- Body -->
              <div style="padding:30px;">
                <p style="font-size:16px; color:#333;">Hi <strong style="color:#0056b3;">{request.user.email}</strong>,</p>

                <p style="font-size:15px; color:#333; line-height:1.6;">
                  Your booking for <strong style="color:#0056b3;">{accommodation.title}</strong> has been successfully confirmed! 🎉
                </p>

                <hr style="border:none; border-top:1px solid #ddd; margin:20px 0;">

                <!-- Booking Details -->
                <table style="width:100%; font-size:15px; color:#333;">
                  <tr>
                    <td style="padding:8px 0;"><strong>🏠 Room:</strong></td>
                    <td style="padding:8px 0;">{available_room.room_number}</td>
                  </tr>
                  <tr>
                    <td style="padding:8px 0;"><strong>💰 Original Price:</strong></td>
                    <td style="padding:8px 0;">€{booking.original_price:.2f}</td>
                  </tr>
                  <tr>
                    <td style="padding:8px 0;"><strong>🎁 Discount Applied:</strong></td>
                    <td style="padding:8px 0;">€{booking.discount_applied:.2f}</td>
                  </tr>
                  <tr>
                    <td style="padding:8px 0;"><strong>✅ Final Price:</strong></td>
                    <td style="padding:8px 0; color:#198754; font-weight:600;">€{booking.final_price:.2f}</td>
                  </tr>
                </table>

                <div style="margin-top:25px; background:#e8f5e9; border-left:5px solid #198754; padding:15px 20px; border-radius:8px;">
                  <p style="margin:0; color:#155724; font-size:15px;">
                    💳 Please pay the total amount <strong>on arrival</strong> during check-in.
                  </p>
                </div>

                <p style="margin-top:25px; color:#555; font-size:14px;">
                  For any queries, please contact our team at <a href="mailto:studentaccommodation@nci.ie" style="color:#0056b3;">studentaccommodation@nci.ie</a>.
                </p>

                <hr style="border:none; border-top:1px solid #ddd; margin:25px 0;">

                <!-- Footer -->
                <p style="text-align:center; color:#888; font-size:13px;">
                  Thank you for choosing <strong>Student Accommodation</strong>!<br>
                  We look forward to welcoming you soon. 🌟
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

        import smtplib
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("✅ Styled booking confirmation email sent successfully!")

    except Exception as e:
        print("❌ Email send failed:", e)

    # ✅ Show confirmation page
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


# 👤 Register View (email-based)
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


# 🖼️ Upload Accommodation Image (S3 integrated)
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
