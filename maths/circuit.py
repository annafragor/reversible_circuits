class Circuit:
    def __init__(self, n_lines):
        self.n_lines = n_lines
        self.gates_sequence = []


class ToffoliGate:
    def __init__(self, n, target_line_index, control_lines_indexes=()):
        self.n_lines = n
        self.target_line_index = target_line_index
        self.control_lines_indexes = control_lines_indexes

    def set_control_lines_indexes(self):
        pass

    def set_target_line_index(self):
        pass