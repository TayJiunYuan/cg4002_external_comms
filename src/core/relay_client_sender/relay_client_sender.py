import socket
import json
from src.models.sensor_packet import IMUPacket, ShootPacket
from src.utils.print_color import print_colored, COLORS


class RelayClientSender:
    """Class for TCP Client on Laptop to send sensor data to TCP Server on Ultra 96"""

    def __init__(self, host: str, port: int, player_id: int):
        self.host = host
        self.port = port
        self.player_id = player_id
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
            print_colored(
                f"Relay Client (Sender) P{self.player_id} - Connected to {self.host}:{self.port}",
                COLORS["green"],
            )
        except (socket.error, ConnectionRefusedError) as e:
            print_colored(
                f"Relay Client (Sender) P{self.player_id} - Connection error: {e}",
                COLORS["green"],
            )

    def send_packet(self, packet: IMUPacket | ShootPacket):

        encoded_json = json.dumps(packet).encode("utf-8")
        message_length = f"{len(encoded_json)}_".encode("utf-8")
        try:
            self.socket.sendall(message_length + encoded_json)
            print(
                f"Relay Client (Sender) P{self.player_id} - Sent: {packet}",
                COLORS["green"],
            )
        except socket.error as e:
            print(
                f"Relay Client (Sender) P{self.player_id} - End error: {e}",
                COLORS["green"],
            )
