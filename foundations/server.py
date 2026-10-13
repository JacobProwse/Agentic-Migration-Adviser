import hashlib
import socket
import sys

import framing
from handshake import HandshakeError, Server

HOST = '127.0.0.1'  # loopback address for local testing
PORT = 65432  # initiate port number
CONN_TIMEOUT = 10 # default connection timeout 10s

def server_helper(listener, timeout=CONN_TIMEOUT):
    """Handles connections on given server socket. Timeout applies to each receive on the accepted connection."""
    conn, address = listener.accept()  # accept new connection
    conn.settimeout(timeout)  # set a timeout for the connection
    with conn:
        print(f"Connection from: {address}")
        client_public_key = framing.recv_msg(conn)  # receive public key from client
        ciphertext, shared_secret_server = Server.encaps(client_public_key)  # encapsulate to get ciphertext and shared secret
        framing.send_msg(conn, ciphertext)  # send ciphertext back to client
    return shared_secret_server

def server_program(host=HOST, port=PORT):
    """Setup socket and run program."""
    with socket.create_server((host, port)) as server_socket:
        print(f"Server listening on {server_socket.getsockname()}")
        return server_helper(server_socket) # return the shared secret for verification


if __name__ == '__main__':
    try:
        shared_secret_server = server_program()
    except (ConnectionError, framing.FramingError, TimeoutError, HandshakeError) as e:
        print(e)
        sys.exit(1)
    hashed_shared_secret_server = hashlib.sha256(shared_secret_server).hexdigest()
    print(f"Server hashed shared secret snippet: {hashed_shared_secret_server[:16]}...")  # print only the first 16 hex characters