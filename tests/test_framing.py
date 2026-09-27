import socket
import framing
import pytest

class FakeSocket:
    """Stands in for a socket: each recv() returns the next prepared chunk."""

    def __init__(self, chunks):
        self._chunks = list(chunks)

    def recv(self, bufsize):
        if not self._chunks:
            return b""  # behaves like a cleanly closed connection
        chunk = self._chunks.pop(0)
        assert len(chunk) <= bufsize, "fake returned more bytes than recv asked for"
        return chunk

@pytest.fixture
def socket_pair():
    """A connected pair of sockets, closed after each test."""
    sender, receiver = socket.socketpair()
    receiver.settimeout(2)
    with sender, receiver:
        yield sender, receiver

def test_round_trip(socket_pair):
    """A small payload sent from one end arrives intact at the other."""
    #Arrange | unpack socket pair
    sender, receiver = socket_pair

    #Act | send a message from sender to receiver
    framing.send_msg(sender, b"Hello, world!")
    received = framing.recv_msg(receiver)

    assert received == b"Hello, world!"

def test_realistic_size(socket_pair):
    """Check a payload the size of an ML-KEM public key (1,184 bytes) arrives intact."""
    #Arrange | unpack socket pair & create a payload of 1,184 bytes
    payload = bytes(1184)
    sender, receiver = socket_pair

    #Act | send a message from sender to receiver
    framing.send_msg(sender, payload)

    assert framing.recv_msg(receiver) == payload

def test_message_boundaries(socket_pair):
    """Two different messages sent back to back are received as two separate, correct messages."""
    #Arrange | unpack socket pair
    sender, receiver = socket_pair

    #Act | send two messages from sender to receiver
    framing.send_msg(sender, b"First message")
    framing.send_msg(sender, b"Second message")

    #Assert | receive two messages from receiver
    assert framing.recv_msg(receiver) == b"First message"
    assert framing.recv_msg(receiver) == b"Second message"

def test_fragmented_delivery():
    """recv_msg reassembles a message whose header and payload arrive in pieces."""
    message = b"Fragmented message"
    header = framing.HEADER.pack(len(message))
    fake = FakeSocket([header[:2], header[2:], message[:5], message[5:]])

    assert framing.recv_msg(fake) == message

def test_peer_closes_mid_message(socket_pair):
    """Send a header promising more bytes than you actually send, close the sending end, and check that your clear error is raised."""
    #Arrange | create a socket pair, send a header claiming a length of 12 bytes, but only send 11 bytes and close the sending end
    message = b"Hello world"
    header = framing.HEADER.pack(len(message) + 1)  # Header claims 12 bytes, but only 11 bytes will be sent
    sender, receiver = socket_pair
    sender.sendall(header + message)
    sender.close()
    
    #Act | attempt to receive the message and expect a ConnectionError due to incomplete message
    with pytest.raises(ConnectionError) as exc_info:
        framing.recv_msg(receiver)

def test_oversized_header(socket_pair):
    """Send a header claiming a length above your maximum, and check that it's rejected."""
    #Arrange | create a socket pair, send a header claiming a length above the maximum allowed size
    sender, receiver = socket_pair
    oversized_length = framing.MAX_MESSAGE_LENGTH + 1
    header = framing.HEADER.pack(oversized_length)
    sender.sendall(header)
    sender.close()  # Close the sending end to simulate end of transmission

    #Act | attempt to receive the message and expect a FramingError due to oversized message
    with pytest.raises(framing.FramingError):
        framing.recv_msg(receiver)

def test_empty_payload(socket_pair):
    """Test against an empty payload"""
    #Arrange | unpack socket pair
    sender, receiver = socket_pair

    #Act | send an empty message from sender to receiver
    framing.send_msg(sender, b"")
    received = framing.recv_msg(receiver)

    assert received == b""