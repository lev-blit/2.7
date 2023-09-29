import socket
import tempfile

import pytest

from remote_tech.common.protocol import get_msg
from remote_tech.common.protocol import send_msg


@pytest.mark.usefixtures("server_process")
def test_dir(server_port: int) -> None:
    s = socket.socket()
    s.connect(("127.0.0.1", server_port))
    with tempfile.TemporaryDirectory() as tmpdir:
        send_msg(s, f"DIR {tmpdir}")
        assert get_msg(s) == (True, b"[]")

        files_list = [rf"{tmpdir}\t.txt", rf"{tmpdir}\t2.txt"]
        for filename in files_list:
            open(filename, "w").close()

        s = socket.socket()
        s.connect(("127.0.0.1", server_port))
        send_msg(s, f"DIR {tmpdir}")
        assert get_msg(s) == (True, f"{files_list}".encode())
