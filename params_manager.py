from pathlib import Path
from typing import Any

from variables import get_settings


def replace_value(input_file: Path, param: str, value: Any) -> None:
    output_file = input_file.with_name(input_file.name + ".tmp")
    with (
        open(input_file, "r") as input_file_obj,
        open(output_file, "w") as output_file_obj,
    ):
        for line in input_file_obj:
            line = line.strip()
            if line.startswith(param):
                line = f"{param}={value}"

            output_file_obj.write(line)
            output_file_obj.write("\n")

    output_file.replace(input_file)


def add_options(input_file: Path) -> None:
    output_file = input_file.with_name(input_file.name + ".tmp")
    with open(output_file, "w") as output_file_obj:
        with open(input_file, "r") as input_file_obj:
            for line in input_file_obj:
                line = line.strip()
                if line == "# Simulation Options":
                    break

                output_file_obj.write(line)
                output_file_obj.write("\n")

        settings = get_settings()
        with open(settings.options_file, "r") as settings_file:
            settings_file = settings_file.read()

        output_file_obj.write(settings_file)

    output_file.replace(input_file)
