"""
Python 3.11 version requirement and compatibility check.
"""

import sys

if sys.version_info < (3, 11):
    raise RuntimeError(
        "This project requires Python 3.11 or higher. "
        f"You are using Python {sys.version_info.major}.{sys.version_info.minor}."
    )

print(f"Python version: {sys.version}")
print(f"Version check passed!")
