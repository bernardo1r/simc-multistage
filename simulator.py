import io
import logging
import os
import pty
import subprocess
import sys
from collections.abc import Generator
from pathlib import Path

from termcolor import colored

from constants import Constants
from convert_profileset_to_normal_actors import profileset_to_actor
from detect_outliers import detect_outliers
from params_manager import add_options, replace_value
from remove_profiles import remove_profiles
from variables import Settings, get_settings


class Simulator:
    _current_simulation: int = 0
    _logger: logging.Logger
    _settings: Settings

    def __init__(self) -> None:
        # Create a custom log handler class to print with color correct
        # And with different colors depending of level (?)
        self._logger = logging.getLogger("Simulator")
        self._logger.propagate = False
        self._logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                colored("%(asctime)s :: %(levelname)s :: %(message)s", "green"),
                datefmt="%Y/%m/%d %H:%M:%S",
            )
        )
        self._logger.addHandler(handler)
        self._settings = get_settings()

    def _simulate_iter(self, name: Path) -> None:
        self._logger.info(
            f"Starting simulation {self._current_simulation + 1}/{len(self._settings.stages)}"
        )
        executable_path = Path(self._settings.simc_executable).resolve().as_posix()
        master, slave = pty.openpty()
        proc = subprocess.Popen(
            [f"{executable_path}", name.as_posix()],
            stdout=slave,
            stderr=subprocess.DEVNULL,
            close_fds=True,
        )
        os.close(slave)

        buf = io.BytesIO()
        reports_junk = Constants.REPORTS_JUNK.encode()
        with os.fdopen(master, "rb", buffering=0) as file:
            while True:
                try:
                    chunk = file.read(1)
                except OSError:
                    break
                if not chunk:
                    break

                buf.write(chunk)
                if reports_junk in buf.getvalue():
                    break
                elif b"\n" in chunk or b"\r" in chunk:
                    os.write(1, buf.getvalue())
                    sys.stdout.flush()
                    buf.truncate(0)

            while True:
                try:
                    if not file.read(4096):
                        break
                except OSError:
                    break

        proc.wait()

    def simulate(self, name: Path) -> Generator[None]:
        name_first = name
        next_name = name
        end = False
        for stage_idx, stage in enumerate(self._settings.stages):
            if stage_idx == 0:
                add_options(name)
                replace_value(name, Constants.TARGETS, self._settings.targets)
                replace_value(name, Constants.THREADS, self._settings.threads)

            if stage_idx + 1 == len(self._settings.stages):
                name_temp = name.with_name(f"{name.name}.tmp")
                with open(name_temp, "w") as name_temp_stream:
                    profileset_to_actor(name, name_temp_stream)

                name_temp.replace(name)

                end = True
            else:
                next_name = name.with_name(
                    f"{name_first.stem}_{stage_idx + 2}{name_first.suffix}"
                )

            replace_value(name, Constants.TARGET_ERROR, stage)
            self._simulate_iter(name)

            if end:
                return

            profiles = detect_outliers(Path(Constants.JSON_FILENAME))
            with open(next_name, "w") as next_file:
                remove_profiles(name, profiles, next_file)
            del profiles
            name = next_name

            yield

            self._current_simulation += 1
