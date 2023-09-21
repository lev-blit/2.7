import socket
from types import ModuleType
from typing import Callable, Type

from common.exceptions import InvalidArgumentListException
from common.types import Command


def _try_recv_until_timeout(s: socket.socket, amount: int) -> tuple[bool, bytes]:
    try:
        msg = s.recv(amount)
    except TimeoutError:
        return False, b"Timeout"
    return True, msg


def get_msg(s: socket.socket) -> tuple[bool, str]:
    success, length_bytes = _try_recv_until_timeout(s, 4)
    length_str = length_bytes.decode()

    if not success or not length_str.isdigit():
        # TODO: return invalid length received
        # TODO: cleanup socket?
        return False, length_str

    length = int(length_str)
    success, message = _try_recv_until_timeout(s, length)
    return success, message.decode()


def send_msg(s: socket.socket, msg: str) -> None:
    length = len(str(msg))
    length_str = str(length).zfill(4)
    s.send(f"{length_str}{msg}".encode())


def parse_command(message: str) -> tuple[str, list[str]]:
    """
    Returns the command name and its arguments from the given message.
    If the message doesn't contain a valid command - will return an empty name and empty list of arguments.
    """
    # TODO: given the string 'EXECUTE python -c "import sys; print(sys.version_info)", VVVV
    #  return 'EXECUTE', ['python', '-c', 'import sys; print(sys.version_info)']
    #  same with '' instead of ""
    split_message = message.split(" ")
    if len(split_message) == 0:
        return "", []
    command_name, *arguments = split_message
    return command_name, arguments


def validate_command(
    command_name: str,
    commands_module: ModuleType,
    arguments: list[str],
    *,
    invalid_command_callback: Callable[[str], None],
    invalid_arguments_callback: Callable[[str], None],
) -> tuple[bool, Type[Command] | None]:
    command_class: Type[Command] = getattr(commands_module, command_name.upper(), None)
    if command_name.upper() != command_name or command_class is None:
        invalid_command_callback(f"Received invalid command - {command_name}")
        return False, None

    try:
        command_class.validate_argument_list(*arguments)
    except InvalidArgumentListException as e:
        invalid_arguments_callback(str(e))
        return False, command_class

    return True, command_class
