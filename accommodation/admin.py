from django.contrib import admin
from .models import Owner, Student, Amenity, Accommodation, Room, Booking
from .models import FestivalDiscount



# 🏠 Accommodation Admin
@admin.register(Accommodation)
class AccommodationAdmin(admin.ModelAdmin):
    list_display = ('title', 'city', 'price_per_month', 'owner')
    search_fields = ('title', 'city', 'owner__name')
    list_filter = ('city',)

    def save_model(self, request, obj, form, change):
        """Auto-assign owner if missing."""
        if not obj.owner and request.user.email:
            owner, created = Owner.objects.get_or_create(
                email=request.user.email,
                defaults={'name': request.user.username}
            )
            obj.owner = owner
        obj.save()


# 👨‍🎓 Student Admin
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'email')
    search_fields = ('user__username', 'email')


# 👨‍💼 Owner Admin
@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')
    search_fields = ('name', 'email')


# 🛠️ Amenity Admin
@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# 🏡 Room Admin
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('accommodation', 'room_number', 'status')
    list_filter = ('status', 'accommodation')
    search_fields = ('accommodation__title', 'room_number')


# 📅 Booking Admin
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('student', 'room', 'date_booked')
    list_filter = ('date_booked',)
    search_fields = ('student__user__username', 'room__accommodation__title')
    
    
@admin.register(FestivalDiscount)
class FestivalDiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'percentage', 'start_date', 'end_date', 'active')

