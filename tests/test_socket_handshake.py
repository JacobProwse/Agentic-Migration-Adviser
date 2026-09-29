import socket
from concurrent.futures import ThreadPoolExecutor

import pytest
import oqs

import handshake
from client import client_program
import server
import framing

@pytest.fixture(scope="module")
def shared_secret_length():
    """Expected length of shared key from liboqs."""
    with oqs.KeyEncapsulation(handshake.ALGORITHM) as kem:
        return kem.details["length_shared_secret"]

@pytest.fixture()
def listener_and_port():
    """Creates the server socket (listener) on server.HOST, 0."""
    with socket.create_server((server.HOST, 0)) as listener:
        yield listener, listener.getsockname()[1]

def test_secrets_match(shared_secret_length, listener_and_port):
    """Test server shared secret matches the client shared secret."""
    listener, port = listener_and_port
    with ThreadPoolExecutor(max_workers=1) as executor:
        server_future = executor.submit(server.server_helper, listener)
        client_shared_secret = client_program(host=server.HOST, port=port)
        server_shared_secret = server_future.result(timeout=2)
    assert server_shared_secret == client_shared_secret
    assert len(server_shared_secret) == shared_secret_length

def test_server_rejects_wrong_size_public_key(listener_and_port):
    """Checks the server rejects a client configured with an ML-KEM-512 public key."""
    listener, port = listener_and_port
    with ThreadPoolExecutor(max_workers=1) as executor:
        server_future = executor.submit(server.server_helper, listener)
        with socket.create_connection((server.HOST, port), timeout=2) as client_socket:
            with oqs.KeyEncapsulation("ML-KEM-512") as kem:
                public_key = kem.generate_keypair()
            framing.send_msg(client_socket, public_key)  # send public key to server
            with pytest.raises(handshake.HandshakeError):
                server_future.result(timeout=2)
            with pytest.raises(ConnectionError):
                framing.recv_msg(client_socket)  # server should close without sending