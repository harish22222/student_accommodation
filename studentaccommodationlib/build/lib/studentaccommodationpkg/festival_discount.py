class FestivalDiscountLib:
    """
    🎉 A simple reusable library to apply festival discounts.
    
    Example usage:
    -----------------
    from studentaccommodationpkg.festival_discount import FestivalDiscountLib

    discount_lib = FestivalDiscountLib()
    final_price = discount_lib.apply_discount(100, 10)
    print(final_price)  # Output: 90.0
    """

    def apply_discount(self, amount, discount_percentage):
        """
        Apply a discount percentage to a given amount.

        Parameters:
            amount (float or int): Original amount (e.g., 100)
            discount_percentage (float or int): Discount percentage (e.g., 10)

        Returns:
            float: Final price after discount
        """
        try:
            # ✅ Convert safely to float
            amount = float(amount)
            discount_percentage = float(discount_percentage)

            # ✅ Validate discount range
            if not (0 <= discount_percentage <= 100):
                raise ValueError("Discount percentage must be between 0 and 100.")

            # ✅ Apply discount
            discount = (discount_percentage / 100) * amount
            final_amount = round(amount - discount, 2)

            return final_amount

        except Exception as e:
            print(f"❌ Error applying discount: {e}")
            return amount  # Return original amount if something fails
