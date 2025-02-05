""" 
Run TCP Client (Receiving) on Laptop with dummy data for testing.
Command: 'python3 -m test.tcp_relay_clients.test_tcp_client_receiver' from project root.
Run after starting TCP Server (Sending) on Ultra96.
"""

from src.core.tcp_client_receiver.tcp_client_receiver import TCPClientReceiver


host = str(input("Host: "))
port = int(input("Port: "))

client = TCPClientReceiver(
    host=host,
    port=port,
)

client.connect()

while True:
    client.receive_hp_and_bullets()
