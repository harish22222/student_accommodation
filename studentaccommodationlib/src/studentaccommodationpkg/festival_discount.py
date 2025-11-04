from datetime import date
from decimal import Decimal, ROUND_HALF_UP


class FestivalDiscountLib:
    """
    A reusable library to calculate and manage
    festival-based discounts for accommodations.
    """

    def __init__(self, name, percentage, start_date, end_date, active=True):
        # Store values safely as Decimal
        self.name = name
        self.percentage = Decimal(str(percentage))
        self.start_date = start_date
        self.end_date = end_date
        self.active = active

    def is_active(self):
        """Check if the festival discount is active today."""
        today = date.today()
        return self.active and (self.start_date <= today <= self.end_date)

    def apply_discount(self, price):
        """
        Apply the discount and return the final price.
        """
        price = Decimal(str(price))
        if self.is_active() and self.percentage > 0:
            discount_amount = (self.percentage / Decimal(100)) * price
            discounted_price = price - discount_amount
            return discounted_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def get_discount_amount(self, price):
        """Return only the discount amount."""
        price = Decimal(str(price))
        if self.is_active() and self.percentage > 0:
            discount_amount = (self.percentage / Decimal(100)) * price
            return discount_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return Decimal('0.00')
