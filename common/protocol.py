from __future__ import annotations

import socket


def get_msg(s: socket.socket) -> tuple[bool, str]:
    length_str = s.recv(4).decode()
    if not length_str.isdigit():
        # TODO: return invalid length received
        # TODO: cleanup socket?
        return False, "Error"

    length = int(length_str)
    message = s.recv(length)
    return True, message.decode()


def send_msg(s: socket.socket, msg: str) -> None:
    length = len(str(msg))
    length_str = str(length).zfill(4)
    s.send(f"{length_str}{msg}".encode())
