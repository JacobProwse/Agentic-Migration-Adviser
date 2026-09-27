from handshake import Client, Server, HandshakeError
import pytest

FIPS_PUBLIC_KEY_SIZE = 1184
FIPS_PRIVATE_KEY_SIZE = 2400
FIPS_SHARED_SECRET_SIZE = 32
FIPS_CIPHERTEXT_SIZE = 1088

def test_shared_secret_matches():
    """Verify both sides derive the same shared secret after decapsulation."""
    #Arrange
    client = Client()
    server = Server()
    #Act
    ciphertext, shared_secret_server = server.encaps(client.public_key)
    shared_secret_receiver = client.decaps(ciphertext)
    #Assert
    assert shared_secret_receiver == shared_secret_server

def test_tamper_detection():
    """Verify that tampering with the ciphertext results in a different shared secret after decapsulation."""
    #Arrange
    client = Client()
    server = Server()
    ciphertext, shared_secret_server = server.encaps(client.public_key)
    #Act
    ciphertext_tampered = bytearray(ciphertext)
    ciphertext_tampered[0] ^= 0x01  # Flip the last bit of the first byte to simulate tampering
    shared_secret_receiver = client.decaps(bytes(ciphertext_tampered))
    #Assert
    assert shared_secret_receiver != shared_secret_server

def test_public_key_size():
    """Verify that the key sizes are as expected per FIPS standards."""
    #Arrange#Act
    client = Client()
    #Assert
    assert len(client.public_key) == FIPS_PUBLIC_KEY_SIZE  # Public key size is 1,184 bytes

def test_private_key_size():
    """Verify that the key sizes are as expected per FIPS standards."""
    #Arrange#Act
    client = Client()
    #Assert
    assert client.private_key_len == FIPS_PRIVATE_KEY_SIZE  # Private key size is 2,400 bytes

def test_shared_secret_size():
    """Verify that the shared secret size is as expected per FIPS standards."""
    #Arrange
    client = Client()
    server = Server()
    #Act
    _, shared_secret_server = server.encaps(client.public_key)
    #Assert
    assert len(shared_secret_server) == FIPS_SHARED_SECRET_SIZE  # Shared secret size is 32 bytes

def test_ciphertext_size():
    """Verify that the ciphertext size is as expected per FIPS standards."""
    #Arrange
    client = Client()
    server = Server()
    #Act
    ciphertext, _ = server.encaps(client.public_key)
    #Assert
    assert len(ciphertext) == FIPS_CIPHERTEXT_SIZE  # Ciphertext size is 1,088 bytes

def test_diff_handshakes_give_diff_secrets():
    """Verify that two separate handshakes yield different shared secrets."""
    #Arrange
    client1 = Client()
    server1 = Server()
    client2 = Client()
    server2 = Server()
    #Act
    _, shared_secret_server1 = server1.encaps(client1.public_key)
    _, shared_secret_server2 = server2.encaps(client2.public_key)
    #Assert
    assert shared_secret_server1 != shared_secret_server2

def test_ciphertext_error():
    # Arrange
    client = Client()
    # Assert
    with pytest.raises(HandshakeError):
        client.decaps(b"wrong ciphertext size") # Act


def test_public_key_error():
    # Assert
    with pytest.raises(HandshakeError):
        Server.encaps(b"wrong key size") # Act