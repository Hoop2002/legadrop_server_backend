import random
import string


def output_id_generator():
    alphabet = string.ascii_letters + string.digits
    remaining = "output_" + "".join(random.choice(alphabet) for _ in range(24))
    return remaining
