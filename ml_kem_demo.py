import oqs

algorithm = "ML-KEM-768"

# Step 1: Recipient generates a key pair
with oqs.KeyEncapsulation(algorithm) as recipient:
    recipient_public_key: bytes = recipient.generate_keypair()
    recipient_private_key: bytes = recipient.export_secret_key()

print(f"KEM public key:  {len(recipient_public_key)} bytes")   # 1184
print(f"KEM private key: {len(recipient_private_key)} bytes")  # 2400