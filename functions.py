import random


def random_key_gen(length=16):
    chars = 'abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    password = ''
    for i in range(length):
        password += random.choice(chars)
    return password
