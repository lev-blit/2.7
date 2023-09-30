import argparse
import socket
from functools import partial
from typing import Sequence

from .common import commands
from .common.protocol import get_msg
from .common.protocol import parse_command
from .common.protocol import recv_custom_amount
from .common.protocol import send_msg
from .common.protocol import validate_command


def get_server_socket(ip: str, port: int) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    return sock


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--server-port",
        help="the port to connect to on the server",
        type=int,
        dest="server_port",
        default=8080,
    )
    parser.add_argument(
        "--server-ip",
        help="the ip of the server",
        dest="server_ip",
        default="127.0.0.1",
    )
    args = parser.parse_args(argv)
    done = False

    try:
        while not done:
            message = input("Enter message: ")
            command_name, arguments = parse_command(message)
            if command_name != "EXIT":
                valid_command, command_class = validate_command(
                    command_name,
                    commands,
                    arguments,
                    invalid_command_callback=print,
                    invalid_arguments_callback=print,
                )
                if not valid_command:
                    continue
            else:
                command_class = None

            sock = get_server_socket(args.server_ip, args.server_port)
            send_msg(sock, message)
            if command_class is not None and command_class.MULTI_STAGED:
                success, response = command_class(*arguments).multi_stage_recv(
                    partial(get_msg, sock),
                    partial(recv_custom_amount, sock),
                )
            else:
                success, response = get_msg(sock)
            sock.close()
            print(response.decode())
            done = command_name == "EXIT" or not success
    except ConnectionError as e:
        print(f"Couldn't connect to server - {e}")
    finally:
        print("Exiting...")


if __name__ == "__main__":
    main()
