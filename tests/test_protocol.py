import io
import sys
from typing import Any

import pytest

from common.commands import Command
from common.exceptions import InvalidArgumentListException
from common.protocol import parse_command
from common.protocol import validate_command


@pytest.mark.parametrize(
    ("message", "expected_response"),
    (
        ("", ("", [])),
        ("command", ("command", [])),
        ("command arg1 arg2 arg3", ("command", ["arg1", "arg2", "arg3"])),
    ),
)
def test_parse_command(message: str, expected_response: tuple[str, list[str]]) -> None:
    assert parse_command(message) == expected_response


class MOCK_COMMAND(Command):
    @classmethod
    def validate_argument_list(cls, *args: str) -> None:
        if len(args) > 2:
            raise InvalidArgumentListException()

    @classmethod
    def help_message(cls) -> str:
        return "help message"

    def validate_pre_run(self) -> None:
        pass

    def run(self) -> Any:
        pass


@pytest.mark.parametrize(
    ("command_name", "args", "expected_value"),
    (
        ("MOCK_COMMAND", [], (True, MOCK_COMMAND)),
        ("MOCK_COMMAND", [1, 2, 3], (False, MOCK_COMMAND)),
        ("invalid", [], (False, None)),
    ),
)
def test_validate_command(
    command_name: str, args: list[str], expected_value: tuple[bool, type[Command] | None]
) -> None:
    ret = validate_command(
        command_name,
        sys.modules[__name__],
        args,
        invalid_command_callback=lambda _: None,
        invalid_arguments_callback=lambda _: None,
    )
    assert ret == expected_value


def test_validate_command_invalid_command_callback():
    sio = io.StringIO()
    validate_command(
        "invalid_command",
        None,  # type: ignore
        [],
        invalid_command_callback=lambda *args: print(*args, file=sio),
        invalid_arguments_callback=lambda _: None,
    )

    assert sio.getvalue() == "Received invalid command - invalid_command\n"


def test_validate_command_invalid_argument_callback():
    sio = io.StringIO()
    validate_command(
        "MOCK_COMMAND",
        sys.modules[__name__],
        ["1", "2", "3"],
        invalid_command_callback=lambda _: None,
        invalid_arguments_callback=lambda *args: print(*args, file=sio),
    )

    assert sio.getvalue() == "\nhelp message\n"
