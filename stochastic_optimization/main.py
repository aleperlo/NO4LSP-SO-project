import os
from Instances import Hospital
from Solvers import Tabu

# toy -> 40
# 01 -> 200
# 02 -> 200

data_dir = "stochastic_optimization/data/ihtc2024_test_dataset"
# for n in [1, 2, 3, 4]:
file_name = f"toy.json"
file_path = os.path.join(data_dir, file_name)

hospital = Hospital(file_path)

solver = Tabu(40, 1, hospital)
penalty = solver.solve(500)

print(penalty)
hospital.json_dump(
    f"stochastic_optimization/results/sol_toy.json",
    f"stochastic_optimization/logs/toy.csv"
)

