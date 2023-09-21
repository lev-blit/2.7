import glob
import os
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
