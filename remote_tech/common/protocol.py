import socket
from types import ModuleType
from typing import Any
from typing import Callable
from typing import Type

from remote_tech.common.commands import Command
from remote_tech.common.exceptions import InvalidArgumentListException


def _try_recv_until_timeout(s: socket.socket, amount: int) -> tuple[bool, bytes]:
    try:
        msg = s.recv(amount)
    except TimeoutError:
        return False, b"Timeout"
    return True, msg


def get_msg(s: socket.socket) -> tuple[bool, bytes]:
    success, length_str = recv_custom_amount(s, 4)

    if not success or not length_str.isdigit():
        # TODO: cleanup socket?
        return False, length_str

    length = int(length_str)
    return recv_custom_amount(s, length)


def recv_custom_amount(s: socket.socket, amount: int) -> tuple[bool, bytes]:
    success, message = _try_recv_until_timeout(s, amount)
    return success, message


def send_msg(s: socket.socket, msg: Any, *, send_length: bool = True) -> None:
    msg_to_send = msg if isinstance(msg, bytes) else str(msg).encode()
    if not send_length:
        s.send(msg_to_send)
        return

    length = len(msg_to_send)
    length_to_send = str(length).zfill(4).encode()
    s.send(length_to_send + msg_to_send)


def parse_command(message: str) -> tuple[str, list[str]]:
    """
    Returns the command name and its arguments from the given message.
    If the message doesn't contain a valid command -
    will return an empty name and empty list of arguments.
    """
    # TODO: given the string 'EXECUTE python -c "import sys; print(sys.version_info)", VVVV
    #  return 'EXECUTE', ['python', '-c', 'import sys; print(sys.version_info)']
    #  same with '' instead of ""
    #  ^^ could probably implemented with sending "len(arg)arg" for each arg instead of just the entire data
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
    command_class: Type[Command] | None = getattr(commands_module, command_name.upper(), None)
    if command_name.upper() != command_name or command_class is None:
        invalid_command_callback(f"Received invalid command - {command_name}")
        return False, None

    try:
        command_class.validate_argument_list(*arguments)
    except InvalidArgumentListException as e:
        invalid_arguments_callback(f"{e}\n{command_class.help_message()}")
        return False, command_class

    return True, command_class
