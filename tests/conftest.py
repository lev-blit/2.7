import os
import socket
import subprocess
import sys
import tempfile
from typing import Iterator

import pytest


@pytest.fixture
def server_port() -> int:
    return 9090


@pytest.fixture()
def server_process(server_port: int) -> Iterator[subprocess.Popen[bytes]]:
    process = subprocess.Popen(
        [sys.executable, "-m", "remote_tech.server", "--port", str(server_port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    yield process
    if process.returncode is None:
        process.terminate()


@pytest.fixture
def server_process_tmpdir(server_port: int) -> Iterator[tuple[subprocess.Popen[bytes], str]]:
    old_path = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        process = subprocess.Popen(
            [sys.executable, "-m", "remote_tech.server", "--port", str(server_port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        yield process, tmpdir
        os.chdir(old_path)
        if process.returncode is None:
            process.terminate()


def client_socket(port: int) -> socket.socket:
    s = socket.socket()
    s.connect(("127.0.0.1", port))
    return s


@pytest.fixture
def client_socket_fixture(server_port: int) -> socket.socket:
    return client_socket(server_port)
