"""
Run Eval Client on Ultra 96 for testing.
Command: 'python3 -m test.eval_client.test_eval_client'.
Run after starting Eval Server. 
"""

from multiprocessing import Queue, Process
from src.core.eval_client.evaluation_client_process import evaluation_client_process


if __name__ == "__main__":

    dummy_packet = {
        "player_id": 1,
        "action": "gun",
        "game_state": {
            "p1": {
                "hp": 10,
                "bullets": 1,
                "bombs": 1,
                "shield_hp": 10,
                "deaths": 1,
                "shields": 1,
            },
            "p2": {
                "hp": 10,
                "bullets": 1,
                "bombs": 1,
                "shield_hp": 10,
                "deaths": 1,
                "shields": 1,
            },
        },
    }

    host = str(input("TEST - Host: "))
    port = int(input("TEST - Port: "))

    to_eval_queue = Queue()
    from_eval_queue = Queue()

    eval_client_process = Process(
        target=evaluation_client_process,
        args=(
            host,
            port,
            to_eval_queue,
            from_eval_queue,
        ),
        daemon=True,
    )

    eval_client_process.start()

    while True:
        print()
        user_input = input('Enter "a" send dummy packet:\n')

        if user_input == "a":
            to_eval_queue.put(dummy_packet)
