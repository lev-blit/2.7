import socket
from typing import Type

# TODO: change to relative/package? have a common package?
from common import commands
from common.exceptions import InvalidArgumentException
from common.protocol import get_msg, send_msg, parse_command, validate_command
from common.types import Command


# TODO: have this be configurable in env/as a cli argument
CLIENT_TIMEOUT_SECONDS = 10


def init_server_socket() -> socket.socket:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # TODO: have the port be configurable in env/as a cli argument
    server_socket.bind(("0.0.0.0", 8080))
    server_socket.listen()

    return server_socket


def run_client_command(
    command_class: Type[Command], arguments: list[str], client_socket: socket.socket
) -> None:
    try:
        result = command_class(*arguments).run()
    except InvalidArgumentException as e:
        send_msg(client_socket, str(e))
        return
    else:
        send_msg(client_socket, result)
    finally:
        client_socket.close()


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
                valid_command, command_class = validate_command(
                    command_name,
                    commands,
                    arguments,
                    invalid_command_callback=lambda error_msg: send_msg(
                        client_socket, error_msg
                    ),
                    invalid_arguments_callback=lambda error_msg: send_msg(
                        client_socket, error_msg
                    ),
                )
                if not valid_command:
                    continue

                run_client_command(command_class, arguments, client_socket)

    finally:
        print("Exiting...")
        server_socket.close()


if __name__ == "__main__":
    main()
