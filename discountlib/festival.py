# discountlib/festival.py

from datetime import date

class FestivalDiscountLib:
    """
    A simple reusable library to calculate and manage
    festival-based discounts for accommodations.
    """

    def __init__(self, name, percentage, start_date, end_date, active=True):
        self.name = name
        self.percentage = percentage
        self.start_date = start_date
        self.end_date = end_date
        self.active = active

    def is_active(self):
        """Check if the discount is currently valid."""
        today = date.today()
        return self.active and (self.start_date <= today <= self.end_date)

    def apply_discount(self, price):
        """Apply the discount and return the discounted price."""
        if self.is_active():
            discount_amount = (self.percentage / 100) * price
            return round(price - discount_amount, 2)
        return price

    def get_discount_amount(self, price):
        """Return only the discount amount."""
        if self.is_active():
            return round((self.percentage / 100) * price, 2)
        return 0.0
