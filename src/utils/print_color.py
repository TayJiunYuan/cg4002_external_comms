def print_colored(text, color_code="0"):
    """Prints text in a specified color."""
    # Reset color to default
    RESET_COLOR = "0"
    print(f"\033[{color_code}m{text}\033[{RESET_COLOR}m", flush=True)


# Color codes
COLORS = {
    "red": "31",
    "green": "32",
    "yellow": "33",
    "blue": "34",
    "magenta": "35",
    "cyan": "36",
    "white": "37",
}
