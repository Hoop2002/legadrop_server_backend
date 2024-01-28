import random
import string


def id_generator():
    first = random.choice(string.ascii_uppercase)
    second = random.choice(string.ascii_lowercase)
    third = random.choice(string.digits)
    alphabet = string.ascii_letters + string.digits
    remaining = "".join(random.choice(alphabet) for _ in range(6))
    return first + second + third + remaining
