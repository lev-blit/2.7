import socket
from typing import Type

from common import commands
from common.exceptions import InvalidArgumentListException
from common.protocol import get_msg, send_msg
from common.types import Command

# TODO: have this be an arg to running the client to be able to control which server to connect to
SERVER_IP = "127.0.0.1"
SERVER_PORT = 8080


def main() -> None:
    done = False
    sock = None

    try:
        while not done:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((SERVER_IP, SERVER_PORT))
            message = input("Enter message: ")
            command_name, *arguments = message.split()
            # TODO: don't treat EXIT differently
            if command_name == "EXIT":
                send_msg(sock, message)
                done = True
                continue

            # TODO: extract this parsing to common.extract_command or something of the sorts
            command_class: Type[Command] = getattr(commands, command_name, None)
            if command_class is None:
                print(f"Received invalid command - {command_name}")
                continue

            try:
                command_class.validate_argument_list(*arguments)
            except InvalidArgumentListException as e:
                print(str(e))
                continue

            send_msg(sock, message)
            success, response = get_msg(sock)
            print(response)
            done = not success
    finally:
        print("Exiting...")
        sock.close()



if __name__ == '__main__':
    main()
