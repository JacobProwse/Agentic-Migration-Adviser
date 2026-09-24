import oqs

algorithm = "ML-KEM-768"

# Step 1: Recipient generates a key pair
def keyGen():
    with oqs.KeyEncapsulation(algorithm) as recipient:
        recipient_public_key: bytes = recipient.generate_keypair()
        recipient_private_key: bytes = recipient.export_secret_key()
    return recipient_public_key, recipient_private_key

# Step 2: Sender encapsulates a shared secret
def encaps(recipient_public_key):
    with oqs.KeyEncapsulation(algorithm) as sender:
        ciphertext, shared_secret_sender = sender.encap_secret(recipient_public_key)
    return ciphertext, shared_secret_sender

# Step 3: Recipient decapsulates to recover the shared secret
def decaps(recipient_private_key, ciphertext):
    with oqs.KeyEncapsulation(algorithm, secret_key=recipient_private_key) as recipient_dec:
        shared_secret_receiver = recipient_dec.decap_secret(ciphertext)
    return shared_secret_receiver

if __name__ == "__main__":
    recipient_public_key, recipient_private_key = keyGen()
    print(f"KEM public key:  {len(recipient_public_key)} bytes")   # 1184
    print(f"KEM private key: {len(recipient_private_key)} bytes")  # 2400
    ciphertext, shared_secret_sender = encaps(recipient_public_key)
    print(f"Ciphertext:      {len(ciphertext)} bytes")           # 1088
    print(f"Sender's secret key:   {len(shared_secret_sender)} bytes") # 32
    shared_secret_receiver = decaps(recipient_private_key, ciphertext)
    print(f"Recipient's secret key: {len(shared_secret_receiver)} bytes") # 32