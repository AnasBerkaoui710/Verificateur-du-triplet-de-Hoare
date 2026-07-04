# verifier/utils.py

def format_state(state):
    """
    Formats a state dictionary into a clean string representation.
    Example: {'x': 1, 'y': -2, 'z': 0} -> "x = 1, y = -2, z = 0"
    """
    if not state:
        return "Undefined"
    return ", ".join(f"{k} = {v}" for k, v in sorted(state.items()))

def format_time(seconds):
    """Formats execution time in seconds to a human-readable string (milliseconds or seconds)."""
    if seconds < 0.001:
        return f"{seconds * 1000000:.1f} µs"
    elif seconds < 1.0:
        return f"{seconds * 1000:.2f} ms"
    else:
        return f"{seconds:.3f} s"
