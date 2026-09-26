import socket
import framing
import pytest

@pytest.fixture
def socket_pair():
    """A connected pair of sockets, closed after each test."""
    sender, receiver = socket.socketpair()
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
    """A payload the size of an ML-KEM public key (1,184 bytes) intact."""
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
    assert framing.recv_msg(receiver) == b"First message" and framing.recv_msg(receiver) == b"Second message"

def test_fragmented_delivery():
    """A socketpair delivers everything at once, write raw bytes to the sending end in several pieces, splitting the header or payload partway through.
    Check receive function reassembles the correct message."""
    pass

def test_peer_closes_mid_message():
    """Send a header promising more bytes than you actually send, close the sending end, and check that your clear error is raised."""
    pass

def test_oversized_header():
    """Send a header claiming a length above your maximum, and check that it's rejected."""
    pass

def test_empty_payload():
    """Test against an empty payload"""
    pass