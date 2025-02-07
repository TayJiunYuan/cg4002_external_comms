import socket
import json
from src.models.game_state import HPAndBulletsState
from src.utils.print_color import print_colored, COLORS


class RelayClientReceiver:
    """Class for TCP Client on Laptop receive hp and bullets data from TCP Server on Ultra 96"""

    def __init__(self, host: str, port: int, player_id: int):
        self.host = host
        self.port = port
        self.player_id = player_id
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
            print_colored(
                f"Relay Client (Receiver) P{self.player_id} - Connected to {self.host}:{self.port}",
                COLORS["yellow"],
            )
        except (socket.error, ConnectionRefusedError) as e:
            print_colored(
                f"Relay Client (Receiver) P{self.player_id} - Connection error: {e}",
                COLORS["yellow"],
            )

    def receive_hp_and_bullets(self) -> HPAndBulletsState:
        """Receives a hp and bullets from the server"""
        try:
            # Read message length
            length_data = b""
            while not length_data.endswith(b"_"):
                chunk = self.socket.recv(1)
                if not chunk:
                    raise ConnectionError("Connection lost while receiving length.")
                length_data += chunk

            length = int(length_data[:-1].decode("utf-8"))

            # Read message content
            data = b""
            while len(data) < length:
                chunk = self.socket.recv(length - len(data))
                if not chunk:
                    raise ConnectionError("Connection lost while receiving message.")
                data += chunk
            hp_and_bullets = json.loads(data.decode("utf-8"))
            print_colored(
                f"Relay Client (Receiver) P{self.player_id} - Received: {hp_and_bullets}",
                COLORS["yellow"],
            )
            return hp_and_bullets
        except (ValueError, socket.error, ConnectionError) as e:
            print_colored(
                f"Relay Client (Receiver) P{self.player_id} - Receive error: {e}",
                COLORS["yellow"],
            )
            return None
