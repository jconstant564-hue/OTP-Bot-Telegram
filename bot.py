import re

# validate phone number format

def validate_phone_number(phonenum):
    pattern = r'^\+\d+$'  # start with + followed by digits
    return re.match(pattern, phonenum) is not None

# Example usage
phonenum = input('Enter your phone number: ')
if not validate_phone_number(phonenum):
    print('Invalid phone number format.')
else:
    print('Phone number is valid.')