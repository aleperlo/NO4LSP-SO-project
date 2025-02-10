from Instances.Hospital import Hospital, ActionError
import copy

class Tabu:
    def __init__(self, tabu_size: int, factor: float, hospital: Hospital):
        self.tabu_size = tabu_size
        self.tabu_list = []
        self.factor = factor
        self.hospital = hospital

    def solve(self, max_iter:int):
        best_penalty, _ = self.hospital.compute_penalty()
        current_penalty = best_penalty
        for i in range(max_iter):
            neighboring_actions = self.hospital.get_neighboring_moves()
            next_action = None
            next_penalty = float("inf")
            for neighboring_action in neighboring_actions:
                try:
                    p, _ = self.hospital.apply_action(neighboring_action)
                except ActionError as e:
                    continue
                if neighboring_action in self.tabu_list and p >= best_penalty * self.factor:
                    continue
                if p < next_penalty:
                    next_penalty = p
                    next_action = neighboring_action
            if next_action is None: # TODO
                print(i)
                break
            self.hospital.apply_action(next_action, assign=True)
            current_penalty = next_penalty
            if current_penalty < best_penalty:
                best_penalty = current_penalty
                self.hospital.save_status()
            self.tabu_list.append(next_action)
            if len(self.tabu_list) > self.tabu_size:
                self.tabu_list = self.tabu_list[-self.tabu_size :]
