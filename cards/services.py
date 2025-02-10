import hashlib
import time
import random
from datetime import datetime


class CardNumberGenerator:
    BIN_RANGES = {
        'VISA': '400000',  # 6-digit BIN
        'MASTERCARD': '510000',  # 6-digit BIN
        'AMEX': '340000'  # 6-digit BIN
    }

    @staticmethod
    def generate_unique_number(card_type='VISA'):
        # Get BIN prefix based on card type
        bin_prefix = CardNumberGenerator.BIN_RANGES.get(card_type, '400000')

        # Generate timestamp-based unique identifier
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        random_num = str(random.randint(1000, 9999))

        # Create a unique base string
        base = f"{timestamp}{random_num}"

        # Generate SHA-256 hash
        hash_object = hashlib.sha256(base.encode())
        hash_hex = hash_object.hexdigest()

        # Convert hash to numbers only (take first 9 numeric characters)
        numeric_hash = ''.join(c for c in hash_hex if c.isdigit())[:9]

        # Combine BIN and numeric hash
        partial_number = f"{bin_prefix}{numeric_hash}"

        # Ensure the partial number is the correct length (15 digits for the partial number)
        partial_number = partial_number[:15]

        # Calculate and append check digit
        check_digit = CardNumberGenerator.calculate_luhn_checksum(partial_number)

        return f"{partial_number}{check_digit}"

    @staticmethod
    def calculate_luhn_checksum(number):
        digits = [int(d) for d in str(number)]
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        total = sum(odd_digits)
        for digit in even_digits:
            total += sum(divmod(digit * 2, 10))
        return str((10 - (total % 10)) % 10)

    @staticmethod
    def is_valid_card_number(card_number):
        if not card_number.isdigit():
            return False
        return CardNumberGenerator.calculate_luhn_checksum(card_number[:-1]) == card_number[-1]

    @staticmethod
    def get_card_length(card_type):
        if card_type == 'AMEX':
            return 15
        return 16  # VISA and MASTERCARD
