import socket
from functools import partial
from typing import Any
from typing import Type

from common import commands
from common.exceptions import InvalidArgumentException
from common.protocol import get_msg
from common.protocol import parse_command
from common.protocol import send_msg
from common.protocol import validate_command
from common.types import Command

# TODO: change to relative/package? have a common package?


# TODO: have this be configurable in env/as a cli argument
CLIENT_TIMEOUT_SECONDS = 10


def init_server_socket() -> socket.socket:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # TODO: have the port be configurable in env/as a cli argument
    server_socket.bind(("0.0.0.0", 8080))
    server_socket.listen()

    return server_socket


def run_client_command(command_class: Type[Command], arguments: list[str]) -> Any:
    try:
        result = command_class(*arguments).run()
    except InvalidArgumentException as e:
        result = str(e)
    return result


def main() -> None:
    server_socket = init_server_socket()
    done = False

    try:
        while not done:
            client_socket, client_address = server_socket.accept()
            client_socket.settimeout(CLIENT_TIMEOUT_SECONDS)
            print(f"Received new connection from {client_address}")
            success, message = get_msg(client_socket)
            if not success:
                print(f"Received invalid message={message.decode()}")
                send_msg(client_socket, "Invalid message sent")
                client_socket.close()
                continue
            print(f"Received message={message.decode()}")
            command_name, arguments = parse_command(message.decode())

            if command_name == "EXIT":
                result = "Server shutting down..."
                command_class = None
                done = True
            else:
                valid_command, command_class = validate_command(
                    command_name,
                    commands,
                    arguments,
                    invalid_command_callback=partial(send_msg, client_socket),
                    invalid_arguments_callback=partial(send_msg, client_socket),
                )
                if not valid_command or command_class is None:
                    continue

                result = run_client_command(command_class, arguments)

            if command_class is not None and command_class.MULTI_STAGED:
                # TODO: prettier
                def _send(msg: Any, sock=client_socket) -> None:
                    send_msg(sock, msg)

                def _send_no_length(msg: Any, sock=client_socket) -> None:
                    send_msg(sock, msg, send_length=False)

                command_class(*arguments).multi_stage_send(
                    _send,
                    _send_no_length,
                )
            else:
                send_msg(client_socket, result)

    finally:
        print("Exiting...")
        server_socket.close()


if __name__ == "__main__":
    main()
