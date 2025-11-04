from datetime import date
from decimal import Decimal  # ✅ add this import

class FestivalDiscountLib:
    """
    A simple reusable library to calculate and manage
    festival-based discounts for accommodations.
    """

    def __init__(self, name, percentage, start_date, end_date, active=True):
        self.name = name
        self.percentage = Decimal(str(percentage))  # ✅ store as Decimal
        self.start_date = start_date
        self.end_date = end_date
        self.active = active

    def is_active(self):
        today = date.today()
        return self.active and (self.start_date <= today <= self.end_date)

    def apply_discount(self, price):
        """Apply the discount and return the discounted price."""
        price = Decimal(str(price))  # ✅ convert to Decimal
        if self.is_active():
            discount_amount = (self.percentage / Decimal(100)) * price
            return round(price - discount_amount, 2)
        return price

    def get_discount_amount(self, price):
        """Return only the discount amount."""
        price = Decimal(str(price))  # ✅ convert to Decimal
        if self.is_active():
            return round((self.percentage / Decimal(100)) * price, 2)
        return Decimal('0.00')
