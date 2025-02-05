import socket
import json
from src.models.game_state import HPAndBulletsState


class TCPClientReceiver:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
            print(f"Receiver Client - Connected to {self.host}:{self.port}")
        except (socket.error, ConnectionRefusedError) as e:
            print(f"Receiver Client - Connection error: {e}")

    def receive_hp_and_bullets(self) -> HPAndBulletsState:
        """Receives a hp and bullets from the server"""
        try:
            # Read message length
            length_data = b""
            while not length_data.endswith(b"_"):
                chunk = self.socket.recv(1)
                if not chunk:
                    raise ConnectionError(
                        "Receiver Client - Connection lost while receiving length."
                    )
                length_data += chunk

            length = int(length_data[:-1].decode("utf-8"))

            # Read message content
            data = b""
            while len(data) < length:
                chunk = self.socket.recv(length - len(data))
                if not chunk:
                    raise ConnectionError(
                        "Receiver Client - Connection lost while receiving message."
                    )
                data += chunk
            hp_and_bullets = json.loads(data.decode("utf-8"))
            print("Receiver Client - Received: ", hp_and_bullets)
            return hp_and_bullets
        except (ValueError, socket.error, ConnectionError) as e:
            print(f"Receiver Client - Receive error: {e}")
            return None
