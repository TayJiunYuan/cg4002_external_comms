import socket
from src.core.eval_client.aes_cipher import AESCipher


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
            print(f"Connected to {self.host}:{self.port}")
            self.send_message("hello")
        except (socket.error, ConnectionRefusedError) as e:
            print(f"Connection error: {e}")

    def send_message(self, message: str):
        """Encrypts and sends a message."""
        encrypted_message = self.cipher.encrypt(message)
        message_length = f"{len(encrypted_message)}_".encode("utf-8")
        try:
            self.socket.sendall(message_length + encrypted_message)
            print(f"Sent: {message}")
        except socket.error as e:
            print(f"Send error: {e}")

    def receive_message(self):
        """Receives and decrypts a message from the evaluation server."""
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
            print("Received: ", data.decode("utf-8"))
            return data.decode("utf-8")

        except (ValueError, socket.error, ConnectionError) as e:
            print(f"Receive error: {e}")
            return None
