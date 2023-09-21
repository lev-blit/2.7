import socket


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
