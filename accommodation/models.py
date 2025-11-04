from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from studentaccommodationpkg.festival_discount import FestivalDiscountLib
from decimal import Decimal


# 👨‍💼 Owner Model
class Owner(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name


# 🎉 Festival Discount Model
class FestivalDiscount(models.Model):
    name = models.CharField(max_length=100)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.percentage}%)"

    def is_active(self):
        today = timezone.now().date()
        return self.active and (self.start_date <= today <= self.end_date)


# 🏠 Accommodation Model
class Accommodation(models.Model):
    title = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    price_per_month = models.DecimalField(max_digits=8, decimal_places=2)
    address = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='accommodations/', blank=True, null=True)
    festival_discount = models.ForeignKey(FestivalDiscount, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.title

    def get_final_price(self):
        """Calculate discounted price using FestivalDiscountLib"""
        if self.festival_discount and self.festival_discount.is_active():
            discount_lib = FestivalDiscountLib(
                name=self.festival_discount.name,
                percentage=self.festival_discount.percentage,
                start_date=self.festival_discount.start_date,
                end_date=self.festival_discount.end_date,
                active=self.festival_discount.active
            )
            return discount_lib.apply_discount(self.price_per_month)
        return self.price_per_month

    def get_discount_amount(self):
        """Return only discount amount"""
        if self.festival_discount and self.festival_discount.is_active():
            discount_lib = FestivalDiscountLib(
                name=self.festival_discount.name,
                percentage=self.festival_discount.percentage,
                start_date=self.festival_discount.start_date,
                end_date=self.festival_discount.end_date,
                active=self.festival_discount.active
            )
            return discount_lib.get_discount_amount(self.price_per_month)
        return Decimal('0.00')


# 🛠️ Amenity Model
class Amenity(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# 🏡 Room Model
class Room(models.Model):
    accommodation = models.ForeignKey(Accommodation, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=50)
    status = models.CharField(
        max_length=20,
        choices=[('Available', 'Available'), ('Booked', 'Booked')],
        default='Available'
    )

    def __str__(self):
        return f"{self.accommodation.title} - Room {self.room_number}"


# 👨‍🎓 Student Model
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.user.username


# 📅 Booking Model
class Booking(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    date_booked = models.DateTimeField(auto_now_add=True)

    # 🧮 Pricing details
    original_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    discount_applied = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    final_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.student.user.username} - {self.room.room_number}"

    def save(self, *args, **kwargs):
        """Auto-calculate discount and final price"""
        accommodation = self.room.accommodation
        self.original_price = accommodation.price_per_month
        self.discount_applied = accommodation.get_discount_amount()
        self.final_price = accommodation.get_final_price()
        super().save(*args, **kwargs)
