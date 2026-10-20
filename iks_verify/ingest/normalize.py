import re
import unicodedata


def normalize_devanagari(value: str) -> str:
    """Normalize for comparison while retaining original display text elsewhere."""
    value = unicodedata.normalize("NFC", value)
    value = re.sub(r"[।॥]", " ", value)
    value = re.sub(r"[०-९0-9]+", " ", value)
    return " ".join(value.split())
