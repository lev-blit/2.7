import abc
from typing import Any
from typing import Callable


class Command(abc.ABC):
    MULTI_STAGED = False

    def __init__(self, name: str, *args: Any) -> None:
        # XXX: is this needed?
        self.name = name

    # TODO: is it any? or is it str?
    @classmethod
    @abc.abstractmethod
    def validate_argument_list(cls, *args: Any) -> None:
        """
        A method to validate the argument list given the command.
        This method validates the amount and type of arguments given to the command,
        not whether the arguments themselves are valid for the command being run on a server.
        This method should be used both in clients and in servers.
        """
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def help_message(cls) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def validate_pre_run(self) -> None:
        """
        A method to validate to specific arguments and not just their amount and type.
        This should be used only when running the command, while `validate_argument_list` can be
        used to validate the command on clients before sending it a server to execute.
        This method should only be run on a server, before calling the `run` method.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def run(self) -> Any:
        """Runs the command and returns a tuple of [success, result]"""
        raise NotImplementedError

    if MULTI_STAGED:

        @abc.abstractmethod
        def multi_stage_send(
            self,
            send_with_len_callback: Callable[[Any], None],
            pure_send_callback: Callable[[Any], None],
        ) -> Any:
            raise NotImplementedError

        @abc.abstractmethod
        def multi_stage_recv(
            self,
            get_msg_callback: Callable[[], tuple[bool, bytes]],
            recv_callback: Callable[[int], tuple[bool, bytes]],
        ) -> tuple[bool, bytes]:
            raise NotImplementedError
