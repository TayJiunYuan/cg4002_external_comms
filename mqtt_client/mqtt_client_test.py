from mqtt_client import MQTTClient


def main():
    client = MQTTClient()
    while True:
        user_input = input(
            'Enter "v" to do a visibility request and enter "a" to send a action to visualizer: '
        )
        if user_input == "v":
            print(user_input)
            client.request_visibility(player_id=1)
        if user_input == "a":
            client.send_action(
                player_id=1, action="shoot", opponent_hp_hit=5, opponent_died=False
            )


main()
