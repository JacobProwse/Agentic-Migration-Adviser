import pytest
import ml_kem_demo as ml_kem


"""Verify both sides derive the same shared secret after decapsulation."""
def test_shared_secret_matches():
    #Arrange
    recipient_public_key, recipient_private_key = ml_kem.keyGen()
    #Act
    ciphertext, shared_secret_sender = ml_kem.encaps(recipient_public_key)
    shared_secret_receiver = ml_kem.decaps(recipient_private_key, ciphertext)
    #Assert
    assert shared_secret_receiver == shared_secret_sender

"""Verify that tampering with the ciphertext results in a different shared secret after decapsulation."""
def test_tamper_detection():
    #Arrange
    recipient_public_key, recipient_private_key = ml_kem.keyGen()
    ciphertext, shared_secret_sender = ml_kem.encaps(recipient_public_key)
    #Act
    ciphertext_tampered = bytearray(ciphertext)
    ciphertext_tampered[0] ^= 0x01  # Flip the first bit
    shared_secret_receiver = ml_kem.decaps(recipient_private_key, bytes(ciphertext_tampered))
    #Assert
    assert shared_secret_receiver != shared_secret_sender

"""Verify that the key sizes are as expected per FIPS standards."""
def test_public_key_size():
    #Arrange #Act
    public_key, _ = ml_kem.keyGen()
    #Assert
    assert len(public_key) == 1184  # Public key size is 1,184 bytes

"""Verify that the key sizes are as expected per FIPS standards."""
def test_private_key_size():
    #Arrange #Act
    _, private_key = ml_kem.keyGen()
    #Assert
    assert len(private_key) == 2400  # Private key size is 2,400 bytes

"""Verify that the key sizes are as expected per FIPS standards."""
def test_shared_key_size():
    #Arrange
    public_key, _ = ml_kem.keyGen()
    #Act
    _, shared_secret = ml_kem.encaps(public_key)
    #Assert
    assert len(shared_secret) == 32  # Shared secret size is 32 bytes

"""Verify that the ciphertext size is as expected per FIPS standards."""
def test_ciphertext_size():
    #Arrange
    public_key, _ = ml_kem.keyGen()
    #Act
    ciphertext, _ = ml_kem.encaps(public_key)
    #Assert
    assert len(ciphertext) == 1088  # Ciphertext size is 1,088 bytes