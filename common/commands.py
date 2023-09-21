import glob
import os
import shutil
import subprocess
from typing import Any

from common.exceptions import InvalidArgumentException, InvalidArgumentListException
from common.types import Command


class DIR(Command):
    def __init__(self, *args: Any) -> None:
        super().__init__("DIR")
        self.validate_argument_list(*args)
        self.path = args[0]

    @classmethod
    def validate_argument_list(cls, *args: Any) -> None:
        if not len(args) == 1:
            raise InvalidArgumentListException("DIR only supports one argument")

    def validate_pre_run(self) -> None:
        if not os.path.isdir(self.path):
            raise InvalidArgumentException(f"The given path argument \"{self.path}\" is not a directory")

    def run(self) -> tuple[bool, list[str]]:
        self.validate_pre_run()
        return True, glob.glob(fr"{self.path}\*.*")


class DELETE(Command):
    def __init__(self, *args: Any) -> None:
        super().__init__("DELETE")
        self.validate_argument_list(*args)
        self.path = args[0]

    @classmethod
    def validate_argument_list(cls, *args: Any) -> None:
        if not len(args) == 1:
            raise InvalidArgumentListException("DELETE only supports one argument")

    def validate_pre_run(self) -> None:
        if not os.path.isfile(self.path):
            raise InvalidArgumentException(f"The given path argument \"{self.path}\" is not a file")

    def run(self) -> tuple[bool, str]:
        self.validate_pre_run()
        try:
            os.remove(self.path)
        except OSError as e:
            return False, str(e)
        return True, f"Successfully deleted {self.path}"


class COPY(Command):
    def __init__(self, *args: Any) -> None:
        super().__init__("COPY")
        self.validate_argument_list(*args)
        self.source, self.dest = args

    @classmethod
    def validate_argument_list(cls, *args: Any) -> None:
        if not len(args) == 2:
            raise InvalidArgumentListException("COPY only supports two arguments")
        source, dest = args
        if source == dest:
            raise InvalidArgumentListException("Dest argument must be different from source argument")

    def validate_pre_run(self) -> None:
        if not os.path.isfile(self.source):
            raise InvalidArgumentException(f"The given source argument \"{self.source}\" is not a file")

    def run(self) -> tuple[bool, str]:
        self.validate_pre_run()
        try:
            shutil.copy(self.source, self.dest)
        except OSError as e:
            return False, str(e)
        return True, f"Successfully {self.source} to {self.dest}"


class EXECUTE(Command):
    def __init__(self, *args: Any) -> None:
        super().__init__("EXECUTE")
        self.validate_argument_list(*args)
        self.command = args

    @classmethod
    def validate_argument_list(cls, *args: Any) -> None:
        if not len(args) >= 1:
            raise InvalidArgumentListException("EXECUTE must have at least one argument")

    def validate_pre_run(self) -> None:
        # nothing to validate here
        pass

    def run(self) -> tuple[bool, str]:
        self.validate_pre_run()
        try:
            print(f"{self.command=}")
            exit_code = subprocess.call(self.command)
        except OSError as e:
            return False, str(e)
        return True, f"{self.command} exited with exit code {exit_code}"
