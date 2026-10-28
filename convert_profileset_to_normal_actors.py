import sys
from pathlib import Path
from typing import TextIO


def jump_to_profileset(
    simulation_input_stream: TextIO, simulation_output_stream: TextIO
) -> str:
    name = ""
    while True:
        line = simulation_input_stream.readline()
        simulation_output_stream.write(line)

        if "name=" in line:
            name = line.replace("name=", "").strip()

        if "# Actors" in line:
            return name


def profileset_to_actor(
    simulation_input: Path, simulation_output_stream: TextIO
) -> None:
    with open(simulation_input) as simulation_input_stream:
        char_name = jump_to_profileset(
            simulation_input_stream, simulation_output_stream
        )

        actor_number = 0
        for line in simulation_input_stream:
            if "### Combo " in line:
                actor_number = int(line.replace("### Combo ", "").strip())
                simulation_output_stream.write(
                    f'copy="Combo {actor_number},{char_name}"\n'
                )

            if line.startswith("profileset."):
                line = line.replace(f'profileset."Combo {actor_number}"+=', "")

            simulation_output_stream.write(line)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)

    profileset_to_actor(Path(sys.argv[1]), sys.stdout)
