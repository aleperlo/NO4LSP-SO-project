import os
from Instances.Hospital import Hospital
from Solvers.Tabu import Tabu
import numpy as np

data_dir = "stochastic_optimization/data/ihtc2024_test_dataset"
file_name = "test04.json"
file_path = os.path.join(data_dir, file_name)

hospital = Hospital(file_path)


# toy -> 40
# 01 -> 200
# 02 -> 200


solver = Tabu(200, 1, hospital)
# # hospital.print()
solver.solve(3000)

hospital.load_status()
# hospital.print()
print(hospital.compute_penalty())
hospital.json_dump(
    "stochastic_optimization/data/sol.json"
)

