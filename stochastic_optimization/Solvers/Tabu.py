from Instances.Hospital import Hospital

class Tabu:
    def __init__(self, tabu_size, factor, hospital: Hospital):
        self.tabu_size = tabu_size
        self.tabu_list = []
        self.factor = factor
        self.hospital = hospital
        self.hospital.generate_initial_solution()

    def solve(self, max_iter):
        best_penalty, _ = self.hospital.compute_penalty()
        current_penalty = best_penalty
        for i in range(max_iter):
            neigboring_actions = self.hospital.get_neighboring_moves()
            next_action = None
            next_penalty = float('inf')
            for neigboring_action in neigboring_actions:
                try:
                    p, p_dict = self.hospital.apply_action(neigboring_action)
                except ValueError:
                    continue
                if neigboring_action in self.tabu_list:
                    if p >= best_penalty * self.factor:
                        continue
                if p < next_penalty:
                    next_penalty = p
                    next_action = neigboring_action
                    next_dict = p_dict
            print(next_penalty, str(next_action), end=" - ")
            for key, value in next_dict.items():
                print(key, value, end=" ")
            print()
            self.hospital.apply_action(next_action, assign=True)
            # self.hospital.print()
            current_penalty = next_penalty
            if current_penalty < best_penalty:
                best_penalty = current_penalty
                self.hospital.save_status()
            self.tabu_list.append(next_action)
            if len(self.tabu_list) > self.tabu_size:
                self.tabu_list = self.tabu_list[-self.tabu_size:]