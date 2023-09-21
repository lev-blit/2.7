import socket

from protocol import get_msg, send_msg

# TODO: have this be an arg to running the client to be able to control which server to connect to
SERVER_IP = "127.0.0.1"
SERVER_PORT = 8080


def main() -> None:
    done = False
    sock = None

    while not done:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((SERVER_IP, SERVER_PORT))
        message = input("Enter message: ")
        send_msg(sock, message)
        success, response = get_msg(sock)
        if success:
            print(response)

        done = not success or message == "EXIT"

    print("Exiting...")
    sock.close()


if __name__ == '__main__':
    main()
