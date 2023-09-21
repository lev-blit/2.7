import socket
from typing import Type

# TODO: change to relative/package? have a common package?
from common import commands
from common.exceptions import InvalidArgumentListException, InvalidArgumentException
from common.protocol import get_msg, send_msg, parse_command
from common.types import Command


# TODO: have this be configurable in env/as a cli argument
CLIENT_TIMEOUT_SECONDS = 10


def main() -> None:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # TODO: have the port be configurable in env/as a cli argument
    server_socket.bind(("0.0.0.0", 8080))
    server_socket.listen()

    done = False

    try:
        while not done:
            client_socket, client_address = server_socket.accept()
            client_socket.settimeout(CLIENT_TIMEOUT_SECONDS)
            print(f"Received new connection from {client_address}")
            success, message = get_msg(client_socket)
            if not success:
                print(f"Received invalid {message=}")
                send_msg(client_socket, "Invalid message sent")
                client_socket.close()
                continue
            print(f"Received {message=}")
            command_name, arguments = parse_command(message)

            if command_name == "EXIT":
                result = "Server shutting down..."
                done = True
            else:
                # TODO: extract this parsing to common.extract_command or something of the sorts
                command_class: Type[Command] = getattr(commands, command_name.upper(), None)
                if command_name.upper() != command_name or command_class is None:
                    send_msg(client_socket, f"Received invalid command - {command_name}")
                    continue

                try:
                    command_class.validate_argument_list(*arguments)
                except InvalidArgumentListException as e:
                    send_msg(client_socket, str(e))
                    continue

                try:
                    result = command_class(*arguments).run()
                except InvalidArgumentException as e:
                    send_msg(client_socket, str(e))
                    continue

            send_msg(client_socket, result)
    finally:
        print("Exiting...")
        server_socket.close()


if __name__ == "__main__":
    main()
