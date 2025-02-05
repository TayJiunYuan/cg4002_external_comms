import socket
import json
from src.models.game_state import HPAndBulletsState
from multiprocessing import Queue


class TCPServerSender:
    """Class for TCP Server on Ultra 96 to send hp and bullet data to a TCP client on laptop"""

    def __init__(self, host, port, queue: Queue):
        self.host = host
        self.port = port
        self.queue = queue
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.client_socket = None

    def start(self):
        """Start the server and wait for a single client connection"""
        self.socket.listen(1)
        print(f"Sender Server - Listening on {self.host}:{self.port}")

        try:
            # Accept a single client connection
            client_socket, client_address = self.socket.accept()
            self.client_socket = client_socket
            print(f"Sender Server - Connection established with {client_address}")
            while True:
                hp_and_bullets = self.queue.get()
                self.send_hp_and_bullets(hp_and_bullets)

        except (socket.error, KeyboardInterrupt) as e:
            print(f"Sender Server - Server error: {e}")
        finally:
            self.socket.close()
            print("Sender Server - Server shut down.")

    def send_hp_and_bullets(self, hp_and_bullets: HPAndBulletsState):
        encoded_json = json.dumps(hp_and_bullets).encode("utf-8")
        message_length = f"{len(encoded_json)}_".encode("utf-8")
        try:
            if self.client_socket:
                self.client_socket.sendall(message_length + encoded_json)
                print(f"Sender Client - Sent: {hp_and_bullets}")
        except socket.error as e:
            print(f"Sender Client - End error: {e}")
