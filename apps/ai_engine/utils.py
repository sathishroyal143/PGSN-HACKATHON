"""AI Engine utilities — shared helpers."""
import time
import logging

logger = logging.getLogger('carebridge')


def timer_ms():
    """Return current time in milliseconds for processing time tracking."""
    return int(time.time() * 1000)


def elapsed_ms(start_ms):
    """Return elapsed milliseconds since start_ms."""
    return timer_ms() - start_ms


def clamp(value, min_val, max_val):
    """Clamp a numeric value between min and max."""
    return max(min_val, min(value, max_val))


def safe_float(value, default=0.0):
    """Safely convert to float, returning default on failure."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def truncate_text(text, max_chars=500):
    """Truncate text to max_chars, appending ellipsis if needed."""
    if not text:
        return ''
    return text[:max_chars] + ('…' if len(text) > max_chars else '')


def format_score(score):
    """Round score to 2 decimal places for consistent display."""
    return round(safe_float(score), 2)
