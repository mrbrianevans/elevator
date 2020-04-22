from Elevator.mechanical_control_model import single_simulation
from Elevator.graphs import *

if __name__ == "__main__":
    single_simulation("mysolution", 30, 10, True)
    interpolate_heatmap(*heatmap_comparison_multicored(30, 30, True))
