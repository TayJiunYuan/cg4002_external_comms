"""
Run MQTT Client on Ultra 96 for testing.
Command: 'python3 -m test.mqtt_client.test_mqtt_client' from project root.
Run after starting MQTT Broker and Visualizer MQTT Client. 
"""

from src.core.mqtt_client.mqtt_client import MQTTClient


def main():
    broker = str(input("Broker: "))
    port = int(input("Port: "))
    client = MQTTClient(broker=broker, port=port)
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
