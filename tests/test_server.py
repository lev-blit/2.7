import socket
import subprocess

import pytest

from remote_tech.common.protocol import get_msg
from remote_tech.common.protocol import send_msg


@pytest.mark.usefixtures("server_process")
def test_invalid_message(server_port: int) -> None:
    s = socket.socket()
    s.connect(("127.0.0.1", server_port))
    s.send(b"invalid message")
    response = get_msg(s)
    assert response == (True, b"Invalid message sent")


@pytest.mark.usefixtures("server_process")
def test_invalid_command(server_port: int) -> None:
    s = socket.socket()
    s.connect(("127.0.0.1", server_port))
    send_msg(s, b"invalid message")
    response = get_msg(s)
    assert response == (True, b"Received invalid command - invalid")


def test_exit(server_process: subprocess.Popen, server_port: int) -> None:
    s = socket.socket()
    s.connect(("127.0.0.1", server_port))
    send_msg(s, "EXIT")
    response = get_msg(s)
    assert response == (True, b"Server shutting down...")
    server_process.wait(0.5)
    assert server_process.returncode == 0
