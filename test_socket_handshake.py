from client import client_program
from server import server_helper
import socket
import pytest
from concurrent.futures import ThreadPoolExecutor

HOST = '127.0.0.1'

def test_secrets_match():
    """Test server shared secret matches the client shared secret"""
    with socket.create_server((HOST, 0)) as server_socket:
        port = server_socket.getsockname()[1]
        with ThreadPoolExecutor() as executor:
            server_future = executor.submit(server_helper, server_socket)
            client_shared_secret = client_program(host = HOST, port = port)
            server_shared_secret = server_future.result()
    assert server_shared_secret == client_shared_secret