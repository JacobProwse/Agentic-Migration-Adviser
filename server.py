import socket
import framing
import handshake

HOST = '127.0.0.1'  # loopback address for local testing
PORT = 1025  # initiate port no above 1024

def server_program(host=HOST, port=PORT):
    with socket.create_server((host, port), family=socket.AF_INET, backlog=5) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # allow reuse of the address
        server_socket.listen(5)  # listen for incoming connections
        print(f"Server listening on {server_socket.getsockname()}")

        conn, address = server_socket.accept()  # accept new connection
        print("Connection from: " + str(address))
        while True:
            data = framing.recv_msg(conn)  # receive message
            if not data:
                break
            print("from connected user: " + str(data.decode('utf-8')))
            data = input(' -> ')  # take input
            framing.send_msg(conn, data.encode())  # send message back to client

        conn.close()  # close the connection
        server_socket.close()  # close the listening socket


if __name__ == '__main__':
    server_program()