import socket
import framing
import handshake

def client_program():
    host = '127.0.0.1'  # loopback address for local testing
    port = 1025  # socket server port number
    
    with socket.create_connection((host, port)) as client_socket:
        print(f"Connected to server at {host}:{port}")

        message = input(" -> ")  # take input

        while message.lower().strip() != 'bye':
            framing.send_msg(client_socket, message.encode())  # send message
            raw = framing.recv_msg(client_socket)  # receive response
            if not raw:
                break
            try:
                data = raw.decode('utf-8')
            except UnicodeDecodeError:
                print("Received non-UTF-8 data from server, skipping")
                continue

            print('Received from server: ' + data)  # show in terminal

            message = input(" -> ")  # again take input

        client_socket.close()  # close the connection


if __name__ == '__main__':
    client_program()