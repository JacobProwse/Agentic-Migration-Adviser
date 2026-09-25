import oqs
from collections import defaultdict

algorithm = "ML-KEM-768"

class client:
    def __init__(self, clientNumber, publicKey = None, privateKey = None, sharedKeys = {}):
        self._public_key = publicKey
        self._private_key = privateKey
        self._shared_keys = sharedKeys
        self._client_number = clientNumber

    def get_public_key(self):
        if self._public_key == None:
            self.__keyGen()
        return self._public_key

    def get_client_number(self):
        return self._client_number

    def get_shared_key(self, server):
        server_number = server.get_server_number()
        if server_number not in self._shared_keys:
            self._shared_keys[server_number] = server.request_key(self._client_number, self.get_public_key())
        return self.__decaps(self._private_key, self._shared_keys[server_number])

    # Step 1: Recipient generates a key pair
    def __keyGen(self):
        with oqs.KeyEncapsulation(algorithm) as recipient:
            self._public_key: bytes = recipient.generate_keypair()
            self._private_key: bytes = recipient.export_secret_key()

    # Step 3: Recipient decapsulates to recover the shared secret
    def __decaps(self, recipient_private_key, ciphertext):
        with oqs.KeyEncapsulation(algorithm, secret_key=recipient_private_key) as recipient_dec:
            shared_secret_receiver = recipient_dec.decap_secret(ciphertext)
        return shared_secret_receiver

class server:
    def __init__(self, serverNumber, sharedKeys = {}):
        self._shared_keys = sharedKeys
        self._server_number = serverNumber

    def get_server_number(self):
        return self._server_number

    def get_shared_key(self, client):
        client_number = client.get_client_number()
        if client_number not in self._shared_keys:
            return None
        return self._shared_keys[client_number]

    # Step 2: Sender encapsulates a shared secret
    def __encaps(self, recipient_public_key):
        with oqs.KeyEncapsulation(algorithm) as sender:
            ciphertext, shared_secret_sender = sender.encap_secret(recipient_public_key)
        return ciphertext, shared_secret_sender

    def request_key(self, clientNumber, client_public_key):
        ciphertext, shared_secret_sender = self.__encaps(client_public_key)
        self._shared_keys[clientNumber] = shared_secret_sender
        return ciphertext

if __name__ == "__main__":
    recipient = client(1)
    recipient_public_key = recipient.get_public_key()
    recipient_private_key = recipient._private_key
    print(f"KEM public key:  {len(recipient_public_key)} bytes")   # 1184
    print(f"KEM private key: {len(recipient_private_key)} bytes")  # 2400

    sender = server(1)
    shared_secret_receiver = recipient.get_shared_key(sender)
    ciphertext = recipient._shared_keys[sender.get_server_number()]
    shared_secret_sender = sender.get_shared_key(recipient)


    print(f"Ciphertext:      {len(ciphertext)} bytes")           # 1088
    print(f"Sender's secret key:   {len(shared_secret_sender)} bytes") # 32
    print(f"Recipient's secret key: {len(shared_secret_receiver)} bytes") # 32