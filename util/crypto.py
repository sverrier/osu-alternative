import os
from cryptography.fernet import Fernet

ENV_KEY_NAME = "OSU_ALT_CONFIG_KEY"

# Fallback key stored in the repo. Replace this with a real key string.
# Generate one with:
DEFAULT_KEY = "muOBSkLpHe-KLB-noaqvRCYFfe-hWoFGzHm8TpIfpyY="


def get_encryption_key() -> bytes:
    """
    Returns the encryption key as bytes.
    Prefers env var OSU_ALT_CONFIG_KEY, falls back to DEFAULT_KEY in this file.
    """
    env_key = os.getenv(ENV_KEY_NAME)
    if env_key:
        return env_key.encode()
    return DEFAULT_KEY.encode()


def get_fernet() -> Fernet:
    """Return a Fernet instance using the shared encryption key."""
    return Fernet(get_encryption_key())