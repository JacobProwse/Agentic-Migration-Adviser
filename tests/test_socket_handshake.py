from client import client_program
from server import server_helper
import socket
import pytest
import handshake
import oqs
from concurrent.futures import ThreadPoolExecutor

HOST = '127.0.0.1'

@pytest.fixture(scope="module")
def shared_secret_length():
    """Expected length of shared key from liboqs."""
    with oqs.KeyEncapsulation(handshake.ALGORITHM) as kem:
        shared_secret_length = kem.details["length_shared_secret"]
    return shared_secret_length

def test_secrets_match(shared_secret_length):
    """Test server shared secret matches the client shared secret"""
    with socket.create_server((HOST, 0)) as server_socket:
        port = server_socket.getsockname()[1]
        with ThreadPoolExecutor(max_workers=1) as executor:
            server_future = executor.submit(server_helper, server_socket)
            client_shared_secret = client_program(host=HOST, port=port)
            server_shared_secret = server_future.result(timeout=2)
    assert server_shared_secret == client_shared_secret
    assert len(server_shared_secret) == shared_secret_length