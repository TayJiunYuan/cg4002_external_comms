"""
Run TCP Server (Receiver) for testing on Ultra 96.
Command: 'python3 -m test.tcp_client_sender_server_receiver.test_tcp_server_receiver' from project root.
"""

from src.core.tcp_server_receiver.tcp_server_receiver import TCPServerReceiver

host = str(input("Host: "))
port = int(input("Port: "))

server = TCPServerReceiver(host=host, port=port)
server.start()
