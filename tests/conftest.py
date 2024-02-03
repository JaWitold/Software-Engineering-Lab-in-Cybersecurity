"""
    Dummy conftest.py for software_engineering_lab_in_cybersecurity.

    If you don't know what this is for, just leave it empty.
    Read more about conftest.py under:
    - https://docs.pytest.org/en/stable/fixture.html
    - https://docs.pytest.org/en/stable/writing_plugins.html
"""

import random


# import pytest
def get_random_int():
    """
    Return a random integer between 1 and 2^256
    :return:
    """
    return random.randint(1, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)
