import paho.mqtt.client as mqtt
import json
from typing import Dict

# MQTT Broker Configuration
BROKER = "127.0.0.1"
PORT = 1883

# MQTT Topics
VISIBILITY_RESPONSE_TOPIC = "/visibility/response"
VISIBILITY_REQUEST_TOPIC = "/visibility/request"
ACTION_TOPIC = "/action"


class MQTTClient:
    """A simple MQTT client for handling game-related messages."""

    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self._connect()

    def _connect(self):
        """Connects to the MQTT broker and starts listening."""
        self.client.connect(BROKER, PORT, 60)
        self.client.loop_start()
        self.client.subscribe(VISIBILITY_RESPONSE_TOPIC)

    def _on_connect(self, client: mqtt.Client, userdata, flags, rc: int):
        """Handles connection events."""
        if rc == 0:
            print("MQTT Client - Connected to MQTT Broker")
        else:
            print(f"MQTT Client - Connection failed, return code {rc}")

    def _on_message(self, client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
        """Handles incoming messages."""
        try:
            payload: Dict = json.loads(msg.payload.decode())
            if msg.topic == VISIBILITY_RESPONSE_TOPIC:
                print(f"MQTT Client - Visibility Response: {payload}")
        except json.JSONDecodeError as e:
            print(f"MQTT Client - Error decoding JSON: {e}")

    def _publish(self, topic: str, message: Dict):
        """Publishes a message to the specified MQTT topic."""
        try:
            self.client.publish(topic, json.dumps(message))
            print(f"MQTT Client - Published to {topic}: {message}")
        except Exception as e:
            print(f"MQTT Client - Error publishing to {topic}: {e}")

    def send_action(
        self, player_id: int, action: str, opponent_hp_hit: int, opponent_died: bool
    ):
        """Publishes a player's action to the visualizer."""
        message = {
            "player_id": player_id,
            "action": action,
            "opponent_hp_hit": opponent_hp_hit,
            "opponent_died": opponent_died,
        }
        self._publish(ACTION_TOPIC, message)

    def request_visibility(self, player_id: int):
        """Publishes a visibility request."""
        message = {"player_id": player_id}
        self._publish(VISIBILITY_REQUEST_TOPIC, message)
