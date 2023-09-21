import abc
from typing import Any


class Command(abc.ABC):
    def __init__(self, name: str, *args: Any) -> None:
        # XXX: is this needed?
        self.name = name

    # TODO: is it any? or is it str?
    @classmethod
    def validate_argument_list(cls, *args: Any) -> None:
        """
        A method to validate the argument list given the command.
        This method validates the amount and type of arguments given to the command,
        not whether the arguments themselves are valid for the command being run on a server.
        This method should be used both in clients and in servers.
        """
        raise NotImplementedError

    def validate_pre_run(self) -> None:
        """
        A method to validate to specific arguments and not just their amount and type.
        This should be used only when running the command, while `validate_argument_list` can be used to validate the
        command on clients before sending it a server to execute.
        This method should only be run on a server, before calling the `run` method.
        """
        raise NotImplementedError

    def run(self) -> tuple[bool, Any]:
        """Runs the command and returns a tuple of [success, result]"""
        raise NotImplementedError
