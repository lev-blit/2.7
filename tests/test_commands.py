import os
import socket
import tempfile

import pytest
from conftest import client_socket

from remote_tech.common.protocol import get_msg
from remote_tech.common.protocol import send_msg


@pytest.mark.usefixtures("server_process")
@pytest.mark.parametrize(
    ("command_message", "expected_response"),
    (
        ("DIR", b"DIR only supports one argument\nUsage: DIR {directory_name}"),
        ("DELETE", b"DELETE only supports one argument\nUsage: DELETE {file_name}"),
        ("COPY", b"COPY only supports two arguments\nUsage: COPY {src_file} {dst_location}"),
        ("EXECUTE", b"EXECUTE must have at least one argument\nUsage: EXECUTE {command} [...args]"),
        (
            "TAKE_SCREENSHOT invalid",
            b"TAKE_SCREENSHOT doesn't accept arguments\nUsage: TAKE_SCREENSHOT",
        ),
        (
            "SEND_FILE",
            b"SEND_FILE only supports two arguments\nUsage: SEND_FILE {remote_location} {local_location}",  # noqa: E501
        ),
    ),
)
def test_invalid_argument_list(
    command_message: str,
    expected_response: str,
    client_socket_fixt: socket.socket,
) -> None:
    send_msg(client_socket_fixt, command_message)
    assert get_msg(client_socket_fixt) == (True, expected_response)


@pytest.mark.usefixtures("server_process")
def test_dir(server_port: int) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        s = client_socket(server_port)
        send_msg(s, f"DIR {tmpdir}")
        assert get_msg(s) == (True, b"[]")

        files_list = [rf"{tmpdir}\t.txt", rf"{tmpdir}\t2.txt"]
        for filename in files_list:
            open(filename, "w").close()

        s = client_socket(server_port)
        send_msg(s, f"DIR {tmpdir}")
        assert get_msg(s) == (True, f"{files_list}".encode())


@pytest.mark.usefixtures("server_process")
def test_delete(server_port: int) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = rf"{tmpdir}\file.txt"
        open(file_path, "w").close()
        s = client_socket(server_port)
        send_msg(s, f"DELETE {file_path}")
        assert get_msg(s) == (True, f"Successfully deleted {file_path}".encode())
        assert not os.path.isfile(file_path)

        s = client_socket(server_port)
        send_msg(s, f"DELETE {file_path}")
        assert get_msg(s) == (True, f'The given path argument "{file_path}" is not a file'.encode())
