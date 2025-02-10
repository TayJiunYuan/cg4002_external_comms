import random
from src.utils.print_color import print_colored, COLORS


class DummyAISerivce:
    def __init__(self):
        print_colored("DUMMY AI - AI Service Started", COLORS["blue"])

    def generate_random_action(self):
        actions = ["reload", "shield", "bomb", "badminton", "golf", "fencing", "boxing"]
        action = random.choice(actions)
        print_colored(f"DUMMY AI  - Action detected: {action}", COLORS["blue"])
        return action
