import hashlib
import random
from datetime import datetime


class CardNumberGenerator:
    BIN_RANGES = {
        'VISA': '400000',
        'MASTERCARD': '510000',
        'AMEX': '340000'
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

        # Convert hash to numbers only
        numeric_hash = ''.join(c for c in hash_hex if c.isdigit())

        # Calculate required length for account number
        total_length = 15 if card_type == 'AMEX' else 16
        account_number_length = total_length - len(bin_prefix) - 1  # -1 for checksum

        # Take required number of digits
        account_number = numeric_hash[:account_number_length]

        # Combine BIN and account number
        partial_number = f"{bin_prefix}{account_number}"

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
