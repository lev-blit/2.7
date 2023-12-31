import argparse
import socket
from functools import partial
from typing import Any
from typing import Sequence
from typing import Type

from .common import commands
from .common.commands import Command
from .common.exceptions import InvalidArgumentException
from .common.protocol import get_msg
from .common.protocol import parse_command
from .common.protocol import send_msg
from .common.protocol import validate_command


def init_server_socket(port: int) -> socket.socket:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", port))
    server_socket.listen()
    print(f"Starting server, listening on port {port}")

    return server_socket


def run_client_command(command_class: Type[Command], arguments: list[str]) -> Any:
    try:
        result = command_class(*arguments).run()
    except InvalidArgumentException as e:
        result = str(e)
    return result


def receive_new_command(
    server_socket: socket.socket,
    client_timeout_seconds: float,
) -> tuple[socket.socket | None, str, list[str]]:
    client_socket, client_address = server_socket.accept()
    client_socket.settimeout(client_timeout_seconds)
    print(f"Received new connection from {client_address}")
    success, message = get_msg(client_socket)
    if not success:
        print(f"Received invalid message={message.decode()}")
        send_msg(client_socket, "Invalid message sent")
        client_socket.shutdown(socket.SHUT_WR)
        return None, "", []

    print(f"Received message={message.decode()}")
    command_name, arguments = parse_command(message.decode())
    return client_socket, command_name, arguments


def handle_exit(client_socket: socket.socket) -> None:
    send_msg(client_socket, "Server shutting down...")


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--port",
        help="the port for the server to listen on",
        type=int,
        default=8080,
    )
    parser.add_argument(
        "--client-timeout-seconds",
        help="timeout for client sockets in seconds",
        type=float,
        default=10,
    )
    args = parser.parse_args(argv)

    server_socket = init_server_socket(args.port)
    done = False

    try:
        while not done:
            client_socket, command_name, arguments = receive_new_command(
                server_socket,
                args.client_timeout_seconds,
            )
            if client_socket is None:
                continue

            if command_name == "EXIT":
                handle_exit(client_socket)
                done = True
                continue

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
                command_class(*arguments).multi_stage_send(
                    partial(send_msg, client_socket),
                    partial(send_msg, client_socket, send_length=False),
                )
            else:
                send_msg(client_socket, result)

    finally:
        print("Exiting...")
        server_socket.close()


if __name__ == "__main__":
    main()
