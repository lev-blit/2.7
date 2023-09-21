from __future__ import annotations

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
        return False, "Error"

    length = int(length_str)
    success, message = _try_recv_until_timeout(s, length)
    return success, message.decode()


def send_msg(s: socket.socket, msg: str) -> None:
    length = len(str(msg))
    length_str = str(length).zfill(4)
    s.send(f"{length_str}{msg}".encode())
