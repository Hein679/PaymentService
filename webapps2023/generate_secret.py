import string
import random

# Generate SECRET_KEY for production.
def generate_secret_key():
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.SystemRandom().choice(chars) for _ in range(50))

print(generate_secret_key())
