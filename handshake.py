import oqs

ALGORITHM = "ML-KEM-768"

class HandshakeError(Exception):
    """Custom exception for incorrect key/ciphertext size handed to encaps/decaps"""

class Client:
    def __init__(self):
        """the client generates an ephemeral keypair"""
        with oqs.KeyEncapsulation(ALGORITHM) as kem:
            self._public_key: bytes = kem.generate_keypair()
            self._private_key: bytes = kem.export_secret_key()

    @property
    def public_key(self):
        return self._public_key

    @property
    def private_key_len(self):
        return len(self._private_key)

    def decaps(self, ciphertext):
        """the client decapsulates the ciphertext"""
        with oqs.KeyEncapsulation(ALGORITHM, secret_key=self._private_key) as kem:
            ciphertext_size = len(ciphertext)
            expected_ciphertext_size = kem.details["length_ciphertext"]
            if  ciphertext_size != expected_ciphertext_size:
                raise HandshakeError(f"Received public key size {ciphertext_size} bytes. Expected {expected_ciphertext_size} bytes.")
            return kem.decap_secret(ciphertext)

class Server:
    @staticmethod
    def encaps(client_public_key):
        with oqs.KeyEncapsulation(ALGORITHM) as kem:
            key_size = len(client_public_key)
            expected_key_size = kem.details["length_public_key"]
            if  key_size != expected_key_size:
                raise HandshakeError(f"Received public key size {key_size} bytes. Expected {expected_key_size} bytes.")
            ciphertext, shared_secret_server = kem.encap_secret(client_public_key)
        return ciphertext, shared_secret_server