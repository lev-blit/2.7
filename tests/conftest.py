import socket
import subprocess
import sys
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
def client_socket(server_port: int) -> socket.socket:
    s = socket.socket()
    s.connect(("127.0.0.1", server_port))
    return s
