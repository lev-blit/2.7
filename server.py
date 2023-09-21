import socket

# TODO: change to relative/package? have a common package?
from protocol import get_msg, send_msg


def main() -> None:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 8080))
    server_socket.listen()

    done = False

    try:
        while not done:
            client_socket, client_address = server_socket.accept()
            success, message = get_msg(client_socket)
            if not success:
                send_msg(client_socket, "Invalid message sent")
                client_socket.close()
                continue
            print(f"Received {message=}")
            send_msg(client_socket, f"Received {message=}")
            if message == "EXIT":
                done = True
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
