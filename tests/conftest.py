import subprocess
import sys
from typing import Iterator

import pytest


@pytest.fixture()
def server_process() -> Iterator[subprocess.Popen]:
    process = subprocess.Popen(
        [sys.executable, "../server/server.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    yield process
    if process.returncode is None:
        process.terminate()
