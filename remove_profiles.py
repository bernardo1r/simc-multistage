import sys
from pathlib import Path
from typing import TextIO


def read_profiles(profiles: Path) -> list[str]:
    profiles_read: list[str] = []
    with open(profiles) as file:
        for line in file:
            profiles_read.append(line.strip())

    return profiles_read


def remove_profiles(
    simulation_input: Path,
    profiles: list[str],
    simulation_output_stream: TextIO,
) -> None:
    profiles = sorted(profiles, key=lambda x: int(x.split(" ")[1]))

    removed = 0
    erase = False
    with open(simulation_input) as file:
        for line in file:
            line = line.strip()

            if erase:
                if len(line) == 0:
                    erase = False
                continue

            if removed < len(profiles) and line.startswith("### Combo"):
                profile = line.replace("### ", "")
                if profiles[removed] == profile:
                    removed += 1
                    erase = True
                    continue

            simulation_output_stream.write(line)
            simulation_output_stream.write("\n")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(1)

    simulation_input = Path(sys.argv[1])

    profiles = Path(sys.argv[2])
    profiles = read_profiles(profiles)

    remove_profiles(simulation_input, profiles, sys.stdout)
