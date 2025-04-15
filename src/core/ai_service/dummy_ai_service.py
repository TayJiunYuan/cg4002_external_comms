import random
from src.utils.print_color import print_colored, COLORS


class DummyAIService:
    def __init__(self):
        print_colored("DUMMY AI - AI Service Started", COLORS["blue"])

    def ai_placeholder_func(self, buffer):
        actions = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        action = random.choice(actions)
        print_colored(f"DUMMY AI  - Action detected: {action}", COLORS["blue"])
        return action
