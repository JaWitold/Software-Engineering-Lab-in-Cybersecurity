"""
Module: fill_pky
This module provides function to fill pki with sample data.
"""

import random
import string

from .public_key_infrastructure import PKI

def generate_random_string(length: int = 8) -> str:
    """
    Generate a random string with given length.

    Args:
        lenght (int): Length of generated string.

    Returns:
        str: A random string.
    """
    characters = string.ascii_letters + string.digits

    return ''.join(random.choice(characters) for _ in range(length))

def fill_pki_database_with_keys(pki: PKI, samples: int = 20):
    """
    Fill PKI database with sample keys.

    Args:
        pki (PKI): PKI database object.
        samples (int): Number of generated keys.
    """
    for user_id in range(samples):
        pki.generate_key_for_user(user_id, generate_random_string())
