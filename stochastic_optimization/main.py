import os
from Instances.Hospital import Hospital

data_dir = 'stochastic_optimization/data'
file_name = 'toy.json'
file_path = os.path.join(data_dir, file_name)

with open(file_path, "r") as fp:
    hospital = Hospital(fp)
