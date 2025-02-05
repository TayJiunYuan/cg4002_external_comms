"""
Run Eval Client on Ultra 96 for testing.
Command: 'python3 -m test.eval_client.test_eval_client'.
Run after starting Eval Server. 
"""

from src.core.eval_client.evaluation_client import EvaluationClient


def main():
    host = str(input("Host: "))
    port = int(input("Port: "))
    client = EvaluationClient(host=host, port=port)
    client.connect()

    while True:
        user_input = input('Enter "a" send dummy packet ')
        if user_input:
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
            client.send_game_state_prediction(dummy_packet)
            client.receive_correct_game_state()


main()
