import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class Profile:
    name: str
    lower_bound: float
    upper_bound: float


def remove_profiles(profiles: list[Profile], actor: int) -> list[int]:
    actor_lower_bound = profiles[actor].lower_bound
    to_remove: list[int] = []

    for idx, profile in enumerate(profiles):
        if idx == actor:
            continue

        if profile.upper_bound < actor_lower_bound:
            to_remove.append(idx)

    return to_remove


def make_profile(profile: dict[str, Any]) -> Profile:
    lower = profile["median"] - profile["mean_error"]
    upper = profile["median"] + profile["mean_error"]
    return Profile(name=profile["name"], lower_bound=lower, upper_bound=upper)


def generate_actor(simulation: dict[str, Any]) -> tuple[list[Profile], int]:
    actor_mean = 0
    actor = 0
    profiles: list[Profile] = []
    for idx, profile in enumerate(simulation["sim"]["profilesets"]["results"]):
        profiles.append(make_profile(profile))

        if profile["mean"] > actor_mean:
            actor_mean = profile["mean"]
            actor = idx

    return profiles, actor


def detect_outliers(json_file: Path) -> list[str]:
    with open(json_file) as file:
        simulation = json.load(file)

    profiles, actor = generate_actor(simulation)
    to_remove = remove_profiles(profiles, actor)
    to_remove_names: list[str] = []
    for idx in to_remove:
        to_remove_names.append(profiles[idx].name)

    return to_remove_names


if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.exit(1)

    to_remove_names = detect_outliers(Path(sys.argv[1]))
    for name in to_remove_names:
        print(name)
