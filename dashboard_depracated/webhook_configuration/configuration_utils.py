


def get_random_string(length, include_digits=True):
    import random
    import string
    letters = string.ascii_letters
    if include_digits:
        letters += string.digits
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str
