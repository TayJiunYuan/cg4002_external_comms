import random
from src.utils.print_color import print_colored, COLORS


class DummyAISerivce:

    def generate_random_action(self):
        actions = ["reload", "shield", "bomb", "badminton", "golf", "fencing", "boxing"]
        action = random.choice(actions)
        print_colored(f"Dummy AI Serivce - Action detected: {action}", COLORS["blue"])
        return action
