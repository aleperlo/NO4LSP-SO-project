class Tabu:
    def __init__(self, tabu_size, factor, hospital):
        self.tabu_size = tabu_size
        self.tabu_list = []
        self.factor = factor
        self.hospital = hospital
        self.hospital.generate_initial_solution()

    def solve(self, max_iter):
        best_penalty = self.hospital.compute_penalty()
        current_penalty = best_penalty
        for i in range(max_iter):
            # TODO: Generate neighboring solutions
            neigboring_actions = []
            next_action = None
            next_penalty = float('inf')
            for neigboring_action in neigboring_actions:
                # TODO: Implement method
                p = self.hospital.apply_action(neigboring_action)
                if neigboring_action in self.tabu_list:
                    if p > best_penalty * self.factor:
                        continue
                if p < next_penalty:
                    next_penalty = p
                    next_action = neigboring_action
            # TODO: Implement method
            self.hospital.apply_action(next_action, assign=True)
            current_penalty = next_penalty
            if current_penalty < best_penalty:
                best_penalty = current_penalty
                self.hospital.save_status()
            self.tabu_list.append(next_action)
            if len(self.tabu_list) > self.tabu_size:
                self.tabu_list = self.tabu_list[-self.tabu_size:]