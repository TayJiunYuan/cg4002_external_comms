import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad


class AESCipher:
    def __init__(self, key: bytes):
        self.key = key

    def encrypt(self, plaintext: str):
        """Encrypt using AES in CBC Mode."""
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(
            iv + cipher.encrypt(pad(plaintext.encode("utf-8"), AES.block_size))
        )
