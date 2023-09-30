import socket
import subprocess

import pytest

from remote_tech.common.protocol import get_msg
from remote_tech.common.protocol import send_msg


@pytest.mark.usefixtures("server_process")
def test_invalid_message(client_socket_fixture: socket.socket) -> None:
    client_socket_fixture.send(b"invalid message")
    response = get_msg(client_socket_fixture)
    assert response == (True, b"Invalid message sent")


@pytest.mark.usefixtures("server_process")
def test_invalid_command(client_socket_fixture: socket.socket) -> None:
    send_msg(client_socket_fixture, b"invalid message")
    response = get_msg(client_socket_fixture)
    assert response == (True, b"Received invalid command - invalid")


def test_exit(server_process: subprocess.Popen, client_socket_fixture: socket.socket) -> None:
    send_msg(client_socket_fixture, "EXIT")
    response = get_msg(client_socket_fixture)
    assert response == (True, b"Server shutting down...")
    server_process.wait(0.5)
    assert server_process.returncode == 0
