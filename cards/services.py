import hashlib
import time
import random
from datetime import datetime


class CardNumberGenerator:
    BIN_RANGES = {
        'VISA': '4',
        'MASTERCARD': '5',
        'AMEX': '3'
    }

    @staticmethod
    def generate_unique_number(card_type='VISA'):
        # Get BIN prefix based on card type
        bin_prefix = CardNumberGenerator.BIN_RANGES.get(card_type, '4')

        # Generate timestamp-based unique identifier
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        random_num = str(random.randint(1000, 9999))

        # Create a unique base string
        base = f"{timestamp}{random_num}"

        # Generate SHA-256 hash
        hash_object = hashlib.sha256(base.encode())
        hash_hex = hash_object.hexdigest()

        # Take first 9 digits of hash
        account_number = hash_hex[:9]

        # Combine BIN, account number, and generate check digit
        partial_number = f"{bin_prefix}{account_number}"
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
        return CardNumberGenerator.calculate_luhn_checksum(card_number[:-1]) == card_number[-1]
