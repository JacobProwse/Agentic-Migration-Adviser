from handshake import Client, Server

if __name__ == "__main__":
    #Initialise the client and server
    client = Client()
    server = Server()
    
    #The server encapsulates against the client's public key
    ciphertext, server_shared_secret = server.encaps(client.public_key)
    #The client decapsulates the ciphertext
    client_shared_secret = client.decaps(ciphertext)

    print(f"server's shared secret: {server_shared_secret}")
    print(f"client's shared secret: {client_shared_secret}")