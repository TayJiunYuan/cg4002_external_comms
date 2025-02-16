import socket
import json
from src.models.game_state import HPAndBulletsState
from multiprocessing import Queue
from src.utils.print_color import print_colored, COLORS


class RelayServerSender:
    """Class for TCP Server on Ultra 96 to send hp and bullet data to a TCP client on laptop"""

    def __init__(self, host: str, port: int, player_id: int, to_relay_queue: Queue):
        self.host = host
        self.port = port
        self.player_id = player_id
        self.to_relay_queue = to_relay_queue
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
        )  # Allow reuse of the same port
        self.socket.bind((self.host, self.port))
        self.client_socket = None

    def start(self):
        """Start the server and wait for a single client connection"""
        self.socket.listen(0)
        print_colored(
            f"Relay Server (Sender) P{self.player_id} - Listening on {self.host}:{self.port}",
            COLORS["yellow"],
        )

        while True:
            try:
                # Accept a single client connection
                client_socket, client_address = self.socket.accept()
                self.client_socket = client_socket
                print_colored(
                    f"Relay Server (Sender) P{self.player_id} - Connection established with {client_address}",
                    COLORS["yellow"],
                )
                self.handle_client()

            except (socket.error, KeyboardInterrupt) as e:
                print_colored(
                    f"Relay Server (Sender) P{self.player_id} - Server error: {e}",
                    COLORS["yellow"],
                )
            finally:
                self.socket.close()
                print_colored(
                    f"Relay Server (Sender) P{self.player_id} - Server shut down.",
                    COLORS["yellow"],
                )

    # TODO: Need to implement some kind of client disconnect check so that we can break the loop and close the socket to allow the restarted client to reconnect
    def handle_client(self):
        try:
            while True:
                hp_and_bullets = self.to_relay_queue.get()
                self.send_hp_and_bullets(hp_and_bullets, self.client_socket)
        except (socket.error, ConnectionError) as e:
            print_colored(
                f"Relay Server (Sender) P{self.player_id} - Connection error: {e}",
                COLORS["yellow"],
            )
        finally:
            self.client_socket.close()

    def send_hp_and_bullets(self, hp_and_bullets: HPAndBulletsState, client_socket):
        encoded_json = json.dumps(hp_and_bullets).encode("utf-8")
        message_length = f"{len(encoded_json)}_".encode("utf-8")
        try:
            if client_socket:
                client_socket.sendall(message_length + encoded_json)
                print_colored(
                    f"Relay Server (Sender) P{self.player_id} - Sent: {hp_and_bullets}",
                    COLORS["yellow"],
                )
        except socket.error as e:
            print_colored(
                f"Relay Server (Sender) P{self.player_id} - End error: {e}",
                COLORS["yellow"],
            )
