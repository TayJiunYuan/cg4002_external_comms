from EvaluationClient import EvaluationClient
import json


def main():
    port = input("Enter Port: ")
    client = EvaluationClient(host="127.0.0.1", port=int(port))
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
            client.send_message(json.dumps(dummy_packet))
            client.receive_message()


main()
