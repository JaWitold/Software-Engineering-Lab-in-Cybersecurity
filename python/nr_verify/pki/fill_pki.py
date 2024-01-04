import random
import string

from PKI import PKI

def generate_random_string(length: int = 8):
    characters = string.ascii_letters + string.digits
    
    return ''.join(random.choice(characters) for _ in range(length))

def fill_pki(pki: PKI, samples: int = 20):
    for id in range(samples):
        pki.generate_key_for_user(id, generate_random_string())
