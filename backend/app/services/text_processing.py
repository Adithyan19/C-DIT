"""
Text Processing Module
Validates, sanitizes, and normalizes farmer text descriptions.
"""
import re
import logging

logger = logging.getLogger("c-dit")

MAX_TEXT_LENGTH = 2000

# Local agricultural term replacements
_REPLACEMENTS: dict[str, str] = {
    "paddy": "rice",
    "brinjal": "eggplant",
    "lady finger": "okra",
    "bhindi": "okra",
    "dhan": "rice",
    "gehun": "wheat",
    "makka": "corn maize",
    "aaloo": "potato",
    "tamatar": "tomato",
    "mirch": "chili pepper",
    "aam": "mango",
    "nimbu": "citrus lemon",
    "kela": "banana",
    "angoor": "grape",
}


def sanitize_text(text: str) -> str:
    """Trim, collapse whitespace, remove dangerous characters."""
    text = text.strip()
    text = re.sub(r"[<>]", "", text)  # basic XSS prevention
    text = re.sub(r"\s+", " ", text)  # collapse whitespace
    return text[:MAX_TEXT_LENGTH]


def validate_text_input(text: str | None) -> str:
    """Validate text meets minimum requirements. Raises ValueError if invalid."""
    if not text or len(text.strip()) == 0:
        raise ValueError("Text description is required and cannot be empty.")
    sanitized = sanitize_text(text)
    if len(sanitized) < 5:
        raise ValueError("Text description must be at least 5 characters long.")
    return sanitized


def process_text_input(raw_text: str) -> str:
    """Process raw text input: validate, sanitize, normalize."""
    logger.info(f"Processing text input (length={len(raw_text)})")
    validated = validate_text_input(raw_text)
    normalized = _normalize_agriculture_text(validated)
    logger.info(f"Text processing complete (length={len(normalized)})")
    return normalized


def _normalize_agriculture_text(text: str) -> str:
    """Expand common agricultural abbreviations and standardize spellings."""
    normalized = text.lower()
    for local, standard in _REPLACEMENTS.items():
        normalized = re.sub(rf"\b{re.escape(local)}\b", standard, normalized, flags=re.IGNORECASE)
    return sanitize_text(normalized)
