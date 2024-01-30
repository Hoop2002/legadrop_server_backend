import random
import string


def payment_order_id_generator():
    alphabet = string.ascii_letters + string.digits
    remaining = "payment_order_" + "".join(random.choice(alphabet) for _ in range(64))
    return remaining
