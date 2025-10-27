from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['room']


class AccommodationSearchForm(forms.Form):
    q = forms.CharField(required=False, label='Search')
    city = forms.CharField(required=False)
    max_price = forms.DecimalField(required=False, decimal_places=2, max_digits=8)

