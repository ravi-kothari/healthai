"""
Medical Record Number (MRN) generator.
Generates unique MRN for patients.
"""

import random
import string
from datetime import datetime


def generate_mrn() -> str:
    """
    Generate a unique Medical Record Number (MRN).

    Format: MRN-YYYYMMDD-XXXXX
    Where:
    - YYYYMMDD: Current date
    - XXXXX: 5-digit random number

    Returns:
        str: Generated MRN

    Example:
        >>> mrn = generate_mrn()
        >>> mrn.startswith("MRN-")
        True
    """
    date_part = datetime.now().strftime("%Y%m%d")
    random_part = ''.join(random.choices(string.digits, k=5))

    return f"MRN-{date_part}-{random_part}"


def validate_mrn(mrn: str) -> bool:
    """
    Validate MRN format.

    Args:
        mrn: MRN string to validate

    Returns:
        bool: True if valid, False otherwise

    Example:
        >>> validate_mrn("MRN-20240101-12345")
        True
        >>> validate_mrn("INVALID")
        False
    """
    if not mrn:
        return False

    parts = mrn.split("-")
    if len(parts) != 3:
        return False

    if parts[0] != "MRN":
        return False

    if len(parts[1]) != 8 or not parts[1].isdigit():
        return False

    if len(parts[2]) != 5 or not parts[2].isdigit():
        return False

    return True
