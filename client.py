import socket

from common import commands
from common.protocol import get_msg, send_msg, parse_command, validate_command

# TODO: have this be an arg to running the client to be able to control which server to connect to
SERVER_IP = "127.0.0.1"
SERVER_PORT = 8080


def get_server_socket(ip: str, port: int) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    return sock


def main() -> None:
    done = False

    try:
        while not done:
            message = input("Enter message: ")
            command_name, arguments = parse_command(message)
            if command_name != "EXIT":
                valid_command, _command_class = validate_command(
                    command_name,
                    commands,
                    arguments,
                    invalid_command_callback=print,
                    invalid_arguments_callback=print,
                )
                if not valid_command:
                    continue

            sock = get_server_socket(SERVER_IP, SERVER_PORT)
            send_msg(sock, message)
            success, response = get_msg(sock)
            sock.close()
            print(response)
            done = command_name == "EXIT" or not success
    finally:
        print("Exiting...")


if __name__ == '__main__':
    main()
