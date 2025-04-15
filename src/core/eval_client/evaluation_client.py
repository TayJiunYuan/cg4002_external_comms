import socket
import json
from src.core.eval_client.aes_cipher import AESCipher
from src.models.game_state import GameState, GameStatePrediction
from src.utils.print_color import print_colored, COLORS


class EvaluationClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.cipher = AESCipher(key=b"aaaaaaaaaaaaaaaa")

    def connect(self):
        """Connects to the evaluation server and sends a hello message."""
        try:
            self.socket.connect((self.host, self.port))
            print_colored(
                f"Eval Client - Connected to {self.host}:{self.port}", COLORS["cyan"]
            )
            self._send_message("hello")
        except (socket.error, ConnectionRefusedError) as e:
            print_colored(f"Connection error: {e}", COLORS["cyan"])

    def _send_message(self, message: str):
        """Encrypts and sends a message."""
        encrypted_message = self.cipher.encrypt(message)
        message_length = f"{len(encrypted_message)}_".encode("utf-8")
        try:
            self.socket.sendall(message_length + encrypted_message)
            print_colored(f"Eval Client - Sent: {message}", COLORS["cyan"])
        except socket.error as e:
            print_colored(f"Eval Client - Send error: {e}", COLORS["cyan"])

    def send_game_state_prediction(self, game_state_prediction: GameStatePrediction):
        """Encrypts and sends game state prediction."""
        self._send_message(json.dumps(game_state_prediction))

    def _receive_message(self, timeout=8):
        """Receives and decrypts a message from the evaluation server."""
        try:
            self.socket.settimeout(timeout)  # Set timeout
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
            return data.decode("utf-8")

        except socket.timeout as e:
            print_colored(
                "Eval Client - Receive error: Timeout while receiving message.",
                COLORS["cyan"],
            )
            return None
        except (ValueError, socket.error, ConnectionError) as e:
            print_colored(f"Eval Client - Receive error: {e}", COLORS["cyan"])
            return None
        finally:
            self.socket.settimeout(None)

    def receive_correct_game_state(self) -> GameState:
        """Receives and decrypts a correct game state from the evaluation server."""
        received_message = self._receive_message()
        if received_message == None:  # error from receive_message
            return None
        correct_game_state = json.loads(received_message)
        print_colored(
            f"Eval Client - Received gamestate from eval server: {correct_game_state}",
            COLORS["cyan"],
        )
        return correct_game_state
