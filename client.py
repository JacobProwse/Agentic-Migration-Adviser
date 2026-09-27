import socket
import framing
from handshake import Client, HandshakeError
import server
import hashlib
import sys

def client_program(host=server.HOST, port=server.PORT):
    with socket.create_connection((host, port), timeout=10) as client_socket:
        print(f"Connected to server at {host}:{port}")

        client = Client()
        framing.send_msg(client_socket, client.public_key)  # send public key to server
        ciphertext = framing.recv_msg(client_socket)  # receive ciphertext from server
        shared_secret_client = client.decaps(ciphertext)  # decapsulate to get shared secret
    return shared_secret_client


if __name__ == '__main__':
    try:
        shared_secret_client = client_program()
    except (ConnectionError, framing.FramingError, TimeoutError, HandshakeError) as e:
        print(e)
        sys.exit(1)
    hashed_shared_secret_client = hashlib.sha256(shared_secret_client).hexdigest()
    print(f"Hashed shared secret snippet: {hashed_shared_secret_client[:16]}...")