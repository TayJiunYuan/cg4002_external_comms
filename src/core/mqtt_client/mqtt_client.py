import paho.mqtt.client as mqtt
import json
from typing import Dict
from multiprocessing import Queue
from src.models.visualizer_packet import (
    VisualizerActionPacket,
    VisibilityRequestPacket,
    VisibilityResponsePacket,
)
from src.utils.print_color import print_colored, COLORS

VISIBILITY_RESPONSE_TOPIC = "/visibility/response"
VISIBILITY_REQUEST_TOPIC = "/visibility/request"
ACTION_TOPIC = "/action"


class MQTTClient:
    """A simple MQTT client for handling game-related messages."""

    def __init__(self, broker: str, port: int, from_visualizer_queue: Queue):
        self.client = mqtt.Client()
        self.from_visualizer_queue = from_visualizer_queue
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self._connect(broker=broker, port=port)

    def _connect(self, broker, port):
        """Connects to the MQTT broker and starts listening."""
        self.client.connect(broker, port, 60)
        self.client.loop_start()
        self.client.subscribe(VISIBILITY_RESPONSE_TOPIC)

    def _on_connect(self, client: mqtt.Client, userdata, flags, rc: int):
        """Handles connection events."""
        if rc == 0:
            print_colored("MQTT Client - Connected to MQTT Broker", COLORS["magenta"])
        else:
            print_colored(
                f"MQTT Client - Connection failed, return code {rc}", COLORS["magenta"]
            )

    def _on_message(self, client: mqtt.Client, userdata, msg: mqtt.MQTTMessage):
        """Handles incoming messages."""
        try:
            payload: VisibilityResponsePacket = json.loads(msg.payload.decode())
            if msg.topic == VISIBILITY_RESPONSE_TOPIC:
                print_colored(
                    f"MQTT Client - Visibility Response: {payload}", COLORS["magenta"]
                )
                self.from_visualizer_queue.put(payload)
        except json.JSONDecodeError as e:
            print_colored(f"MQTT Client - Error decoding JSON: {e}", COLORS["magenta"])

    def _publish(self, topic: str, message: Dict):
        """Publishes a message to the specified MQTT topic."""
        try:
            self.client.publish(topic, json.dumps(message))
            print_colored(
                f"MQTT Client - Published to {topic}: {message}", COLORS["magenta"]
            )
        except Exception as e:
            print_colored(
                f"MQTT Client - Error publishing to {topic}: {e}", COLORS["magenta"]
            )

    def send_action(self, action_packet: VisualizerActionPacket):
        """Publishes a player's action to the visualizer."""
        self._publish(ACTION_TOPIC, action_packet)

    def request_visibility(self, visibility_request_packet: VisibilityRequestPacket):
        """Publishes a visibility request."""
        self._publish(VISIBILITY_REQUEST_TOPIC, visibility_request_packet)
