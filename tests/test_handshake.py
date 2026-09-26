from handshake import Client, Server

FIPS_PUBLIC_KEY_SIZE = 1184
FIPS_PRIVATE_KEY_SIZE = 2400
FIPS_SHARED_SECRET_SIZE = 32
FIPS_CIPHERTEXT_SIZE = 1088

def test_shared_secret_matches():
    """Verify both sides derive the same shared secret after decapsulation."""
    #Arrange
    recipient = Client()
    sender = Server()
    #Act
    ciphertext, shared_secret_sender = sender.encaps(recipient.public_key)
    shared_secret_receiver = recipient.decaps(ciphertext)
    #Assert
    assert shared_secret_receiver == shared_secret_sender

def test_tamper_detection():
    """Verify that tampering with the ciphertext results in a different shared secret after decapsulation."""
    #Arrange
    recipient = Client()
    sender = Server()
    ciphertext, shared_secret_sender = sender.encaps(recipient.public_key)
    #Act
    ciphertext_tampered = bytearray(ciphertext)
    ciphertext_tampered[0] ^= 0x01  # Flip the last bit of the first byte to simulate tampering
    shared_secret_receiver = recipient.decaps(bytes(ciphertext_tampered))
    #Assert
    assert shared_secret_receiver != shared_secret_sender

def test_public_key_size():
    """Verify that the key sizes are as expected per FIPS standards."""
    #Arrange#Act
    recipient = Client()
    #Assert
    assert len(recipient.public_key) == FIPS_PUBLIC_KEY_SIZE  # Public key size is 1,184 bytes

def test_private_key_size():
    """Verify that the key sizes are as expected per FIPS standards."""
    #Arrange#Act
    recipient = Client()
    #Assert
    assert recipient.private_key_len == FIPS_PRIVATE_KEY_SIZE  # Private key size is 2,400 bytes

def test_shared_secret_size():
    """Verify that the shared secret size is as expected per FIPS standards."""
    #Arrange
    recipient = Client()
    sender = Server()
    #Act
    _, shared_secret_sender = sender.encaps(recipient.public_key)
    #Assert
    assert len(shared_secret_sender) == FIPS_SHARED_SECRET_SIZE  # Shared secret size is 32 bytes

def test_ciphertext_size():
    """Verify that the ciphertext size is as expected per FIPS standards."""
    #Arrange
    recipient = Client()
    sender = Server()
    #Act
    ciphertext, _ = sender.encaps(recipient.public_key)
    #Assert
    assert len(ciphertext) == FIPS_CIPHERTEXT_SIZE  # Ciphertext size is 1,088 bytes

def test_diff_handshakes_give_diff_secrets():
    """Verify that two separate handshakes yield different shared secrets."""
    #Arrange
    recipient1 = Client()
    sender1 = Server()
    recipient2 = Client()
    sender2 = Server()
    #Act
    _, shared_secret_sender1 = sender1.encaps(recipient1.public_key)
    _, shared_secret_sender2 = sender2.encaps(recipient2.public_key)
    #Assert
    assert shared_secret_sender1 != shared_secret_sender2