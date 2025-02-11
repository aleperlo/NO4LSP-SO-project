import os
from Instances import Hospital
from Solvers import Tabu

instances = [
    {"file": "toy", "max_iter": 2500, "tabu_size": 30},
    {"file": "test01", "max_iter": 2500, "tabu_size": 150},
    {"file": "test02", "max_iter": 2500, "tabu_size": 200},
    {"file": "test03", "max_iter": 2500, "tabu_size": 200},
    {"file": "test04", "max_iter": 2500, "tabu_size": 250},
    # {"file": "test05", "max_iter": 200, "tabu_size": 200},
    # {"file": "test06", "max_iter": 200, "tabu_size": 200},
    # {"file": "test07", "max_iter": 200, "tabu_size": 200},
    # {"file": "test08", "max_iter": 200, "tabu_size": 200},
    # {"file": "test09", "max_iter": 200, "tabu_size": 200},
    # {"file": "test10", "max_iter": 200, "tabu_size": 200},
]


data_dir = "stochastic_optimization/data/ihtc2024_test_dataset"
for i in instances:
    f = i["file"]
    max_iter = i["max_iter"]
    tabu_size = i["tabu_size"]
    
    file_path = os.path.join(data_dir, f"{f}.json")

    hospital = Hospital(file_path)

    solver = Tabu(tabu_size, 1, hospital)
    penalty = solver.solve(max_iter)

    print(f"Penalty: {penalty}")

    hospital.json_dump(
        f"stochastic_optimization/results/sol_{f}.json",
        f"stochastic_optimization/logs/{f}.csv",
    )
