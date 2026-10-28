from pathlib import Path

from simulator import Simulator

file = Path("simulation.simc")
sim = Simulator()
for _ in sim.simulate(file):
    pass
