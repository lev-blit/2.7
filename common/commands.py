import abc
import glob
import os
import shutil
import subprocess
from typing import Any
from typing import Callable

import pyautogui

from common.exceptions import InvalidArgumentException
from common.exceptions import InvalidArgumentListException


class Command(abc.ABC):
    MULTI_STAGED = False

    def __init__(self, *args: str) -> None:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def validate_argument_list(cls, *args: str) -> None:
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


class DIR(Command):
    def __init__(self, *args: Any) -> None:
        super().__init__()
        self.validate_argument_list(*args)
        self.path = args[0]

    @classmethod
    def validate_argument_list(cls, *args: Any) -> None:
        if len(args) != 1:
            raise InvalidArgumentListException("DIR only supports one argument")

    @classmethod
    def help_message(cls) -> str:
        return "Usage: DIR {directory_name}"

    def validate_pre_run(self) -> None:
        if not os.path.isdir(self.path):
            raise InvalidArgumentException(
                f'The given path argument "{self.path}" is not a directory'
            )

    def run(self) -> list[str]:
        self.validate_pre_run()
        return glob.glob(rf"{self.path}\*.*")


class DELETE(Command):
    def __init__(self, *args: Any) -> None:
        super().__init__()
        self.validate_argument_list(*args)
        self.path = args[0]

    @classmethod
    def validate_argument_list(cls, *args: Any) -> None:
        if len(args) != 1:
            raise InvalidArgumentListException("DELETE only supports one argument")

    @classmethod
    def help_message(cls) -> str:
        return "Usage: DELETE {file_name}"

    def validate_pre_run(self) -> None:
        if not os.path.isfile(self.path):
            raise InvalidArgumentException(f'The given path argument "{self.path}" is not a file')

    def run(self) -> str:
        self.validate_pre_run()
        try:
            os.remove(self.path)
        except OSError as e:
            return str(e)
        return f"Successfully deleted {self.path}"


class COPY(Command):
    def __init__(self, *args: Any) -> None:
        super().__init__()
        self.validate_argument_list(*args)
        self.source, self.dest = args

    @classmethod
    def validate_argument_list(cls, *args: Any) -> None:
        if len(args) != 2:
            raise InvalidArgumentListException("COPY only supports two arguments")
        source, dest = args
        if source == dest:
            raise InvalidArgumentListException(
                "Dest argument must be different from source argument"
            )

    @classmethod
    def help_message(cls) -> str:
        return "Usage: COPY {src_file} {dst_location}"

    def validate_pre_run(self) -> None:
        if not os.path.isfile(self.source):
            raise InvalidArgumentException(
                f'The given source argument "{self.source}" is not a file'
            )

    def run(self) -> str:
        self.validate_pre_run()
        try:
            shutil.copy(self.source, self.dest)
        except OSError as e:
            return str(e)
        return f"Successfully {self.source} to {self.dest}"


class EXECUTE(Command):
    def __init__(self, *args: Any) -> None:
        super().__init__()
        self.validate_argument_list(*args)
        self.command = args

    @classmethod
    def validate_argument_list(cls, *args: Any) -> None:
        if len(args) < 1:
            raise InvalidArgumentListException("EXECUTE must have at least one argument")

    @classmethod
    def help_message(cls) -> str:
        return "Usage: EXECUTE {command} [...args]"

    def validate_pre_run(self) -> None:
        # nothing to validate here
        pass

    def run(self) -> str:
        self.validate_pre_run()
        try:
            # TODO: make this non-blocking so other clients will be able to connect while this is running?  # noqa: E501
            #   might be for when we implement multi-client support
            exit_code = subprocess.call(self.command)
        except OSError as e:
            return str(e)
        return f"{self.command} exited with exit code {exit_code}"


class TAKE_SCREENSHOT(Command):
    def __init__(self, *args: Any) -> None:
        super().__init__()
        self.validate_argument_list(*args)
        self.screenshot_path = "screenshot.jpg"

    @classmethod
    def validate_argument_list(cls, *args: Any) -> None:
        if len(args) != 0:
            raise InvalidArgumentListException("TAKE_SCREENSHOT doesn't accept arguments")

    @classmethod
    def help_message(cls) -> str:
        return "Usage: TAKE_SCREENSHOT"

    def validate_pre_run(self) -> None:
        # nothing to validate here
        pass

    def run(self) -> str:
        self.validate_pre_run()
        try:
            pyautogui.screenshot(self.screenshot_path)
        except Exception as e:
            return f"Failed to save screenshot - {e!r}"
        else:
            return f"Screenshot saved to {self.screenshot_path}"


class SEND_FILE(Command):
    MULTI_STAGED = True

    def __init__(self, *args: Any) -> None:
        super().__init__()
        self.validate_argument_list(*args)
        self.source, self.dest = args
        self.file_size: int = -1

    @classmethod
    def validate_argument_list(cls, *args: Any) -> None:
        if len(args) != 2:
            raise InvalidArgumentListException("SEND_FILE only supports two arguments")

    @classmethod
    def help_message(cls) -> str:
        return "Usage: SEND_FILE {remote_location} {local_location}"

    def validate_pre_run(self) -> None:
        if not os.path.isfile(self.source):
            raise InvalidArgumentException(
                f'The given source argument "{self.source}" is not a file'
            )

    def run(self) -> None:
        pass

    # TODO: name this properly
    def multi_stage_send(
        self,
        send_with_len_callback: Callable[[Any], None],
        pure_send_callback: Callable[[Any], None],
    ) -> None:
        send_with_len_callback(str(os.path.getsize(self.source)))
        with open(self.source, "rb") as f:
            pure_send_callback(f.read())

    def multi_stage_recv(
        self,
        get_msg_callback: Callable[[], tuple[bool, bytes]],
        recv_callback: Callable[[int], tuple[bool, bytes]],
    ) -> tuple[bool, bytes]:
        success, length = get_msg_callback()
        if not success:
            return False, b"Failed receiving response from server"
        if not length.isdigit():
            return False, b"Received invalid response from server about file size"

        success, file_data = recv_callback(int(length))
        if not success:
            return False, b"Received invalid response from server about file data"

        with open(self.dest, "wb") as f:
            f.write(file_data)
        return True, f"Successfully saved file to {self.dest}".encode()
