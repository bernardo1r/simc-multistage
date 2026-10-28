import os
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from functools import lru_cache

from dotenv import load_dotenv


class Variables(StrEnum):
    STAGES = "STAGES"
    TARGETS = "TARGETS"
    THREADS = "THREADS"
    OPTIONS_FILE = "OPTIONS_FILE"
    SIMC_EXECUTABLE = "SIMC_EXECUTABLE"


@dataclass(frozen=True)
class Settings:
    stages: list[float]
    targets: int
    threads: int
    options_file: str
    simc_executable: str


def _req(key: Variables) -> str:
    try:
        return os.environ[key]
    except KeyError:
        raise RuntimeError(f"Missing environment variable: {key!s}") from None


def _cast[T: (int, float)](value: str, target: Callable[[str], T], key: str) -> T:
    try:
        return target(value)
    except (ValueError, TypeError) as e:
        raise RuntimeError(
            f"Invalid cast for environment variable {key!s}: {value!r} -> {target.__name__}:"
            f"\n{e}"
            f"\nVariable must be of type {target.__name__}"
        ) from None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    load_dotenv(override=False)

    stages = [x.strip() for x in _req(Variables.STAGES).split(",") if x.strip()]
    if len(stages) == 0:
        raise RuntimeError("Variables 'stages' must have at least one value") from None

    return Settings(
        stages=[_cast(x, float, Variables.STAGES) for x in stages],
        targets=_cast(_req(Variables.TARGETS), int, Variables.TARGETS),
        threads=_cast(_req(Variables.THREADS), int, Variables.THREADS),
        options_file=_req(Variables.OPTIONS_FILE),
        simc_executable=_req(Variables.SIMC_EXECUTABLE),
    )
