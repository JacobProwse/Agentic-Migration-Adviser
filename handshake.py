import oqs

ALGORITHM = "ML-KEM-768"

class Client:
    def __init__(self):
        """the client generates an ephemeral keypair"""
        with oqs.KeyEncapsulation(ALGORITHM) as client:
            self._public_key: bytes = client.generate_keypair()
            self._private_key: bytes = client.export_secret_key()

    @property
    def public_key(self):
        return self._public_key

    @property
    def private_key_len(self):
        return len(self._private_key)

    def decaps(self, ciphertext):
        """the client decapsulates the ciphertext"""
        with oqs.KeyEncapsulation(ALGORITHM, secret_key=self._private_key) as client_dec:
            return client_dec.decap_secret(ciphertext)

class Server:
    @staticmethod
    def encaps(client_public_key):
        
        with oqs.KeyEncapsulation(ALGORITHM) as server:
            ciphertext, shared_secret_server = server.encap_secret(client_public_key)
        return ciphertext, shared_secret_server