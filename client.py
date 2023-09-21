import socket
from typing import Type

from common import commands
from common.exceptions import InvalidArgumentListException
from common.protocol import get_msg, send_msg, parse_command
from common.types import Command

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
            # TODO: don't treat EXIT differently
            if command_name == "EXIT":
                sock = get_server_socket(SERVER_IP, SERVER_PORT)
                send_msg(sock, message)
                sock.close()
                done = True
                continue

            # TODO: extract this parsing to common.extract_command or something of the sorts
            command_class: Type[Command] = getattr(commands, command_name.upper(), None)
            if command_name.upper() != command_name or command_class is None:
                print(f"Received invalid command - {command_name}")
                continue

            try:
                command_class.validate_argument_list(*arguments)
            except InvalidArgumentListException as e:
                print(str(e))
                continue

            sock = get_server_socket(SERVER_IP, SERVER_PORT)
            send_msg(sock, message)
            success, response = get_msg(sock)
            sock.close()
            print(response)
            done = not success
    finally:
        print("Exiting...")


if __name__ == '__main__':
    main()
