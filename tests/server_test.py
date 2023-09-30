import socket
import subprocess
import sys

import pytest
from conftest import client_socket

from remote_tech.common.protocol import get_msg
from remote_tech.common.protocol import send_msg


@pytest.mark.usefixtures("server_process_tmpdir")
def test_invalid_message(client_socket_fixture: socket.socket) -> None:
    client_socket_fixture.send(b"invalid message")
    response = get_msg(client_socket_fixture)
    assert response == (True, b"Invalid message sent")


@pytest.mark.usefixtures("server_process_tmpdir")
def test_invalid_command(client_socket_fixture: socket.socket) -> None:
    send_msg(client_socket_fixture, b"invalid message")
    response = get_msg(client_socket_fixture)
    assert response == (True, b"Received invalid command - invalid")


def test_exit() -> None:
    process = subprocess.Popen(
        [sys.executable, "-m", "remote_tech.server", "--port", "6060"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    c = client_socket(6060)
    send_msg(c, "EXIT")
    response = get_msg(c)
    assert response == (True, b"Server shutting down...")
    process.wait(0.5)
    assert process.returncode == 0
