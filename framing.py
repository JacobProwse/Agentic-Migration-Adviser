import socket
import struct

MAX_MESSAGE_LENGTH = 2**20 # 1MiB cap for message size to prevent DoS attacks whilst allowing for large messages such as McEliece-sized keys
HEADER = struct.Struct("!I")  # Network byte order (big-endian) unsigned int

class FramingError(Exception):
    """Custom exception for framing errors."""

def send_msg(sock: socket.socket, data: bytes) -> None:
    """Send data with a fixed length prefix."""
    if len(data) > MAX_MESSAGE_LENGTH:
        raise ValueError(f"Data size {len(data)} exceeds maximum allowed size of {MAX_MESSAGE_LENGTH} bytes.")
    header = HEADER.pack(len(data))
    sock.sendall(header + data)

def recv_msg(sock: socket.socket) -> bytes:
    """Receive a length-prefixed message. Raises a FramingError if the message size exceeds MAX_MESSAGE_LENGTH."""
    # Read the fixed-size header
    raw_header = _recvn(sock, HEADER.size)
    (msg_len,) = HEADER.unpack(raw_header)
    if msg_len > MAX_MESSAGE_LENGTH:
        raise FramingError(f"Received message size {msg_len} exceeds maximum allowed size of {MAX_MESSAGE_LENGTH} bytes.")

    # Then read exactly msg_len bytes
    return _recvn(sock, msg_len)

def _recvn(sock: socket.socket, n: int) -> bytes:
    """Read exactly n bytes, raising if the connection closes early."""
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("Connection closed before message was complete")
        buf.extend(chunk)
    return bytes(buf)