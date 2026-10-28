from enum import StrEnum

# Divide into different classes the different context constants (?)
# Allow custom filename constants
# solve problem of filename constants being relative no absolute


class Constants(StrEnum):
    TARGETS = "desired_targets"
    TARGET_ERROR = "target_error"
    THREADS = "threads"
    REPORTS_JUNK = "Generating reports"
    JSON_FILENAME = "artifacts/simulation.json"
