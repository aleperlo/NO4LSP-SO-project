import os
from Instances.Hospital import Hospital, PASAction
from Solvers.Tabu import Tabu

data_dir = 'stochastic_optimization/data/ihtc2024_test_dataset'
file_name = 'test01.json'
file_path = os.path.join(data_dir, file_name)

with open(file_path, "r") as fp:
    hospital = Hospital(fp)

# hospital.generate_initial_solution()
# print(hospital.compute_penalty())
# hospital.print()
# hospital.apply_action(a1, assign=True)
# print(hospital.compute_penalty())
# hospital.print()
# hospital.apply_action(a2, assign=True)
# print(hospital.compute_penalty())
# hospital.print()

solver = Tabu(100, 1, hospital)
hospital.print()
solver.solve(100)

hospital.load_status()
hospital.print()
hospital.json_dump('stochastic_optimization/data/ihtc2024_test_dataset/test01_solution.json')