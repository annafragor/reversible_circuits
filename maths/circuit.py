class Circuit:
    def __init__(self, n_lines, visual_gates=(), y_lines=()):
        self.n_lines = n_lines
        self.ys = list(reversed(y_lines))
        self.gates_sequence = []
        self.gates_dict = {}
        if visual_gates:
            self.fill_visual_gates(visual_gates)

    def add_gate(self, target_line_index, control_lines_indexes=()):
        self.gates_sequence.append(
            ToffoliGate(self.n_lines, target_line_index, control_lines_indexes)
        )

    def fill_visual_gates(self, visual_gates):
        for vgate in visual_gates:
            target_line_coord = self.ys.index(vgate.center_point[1])
            control_line_indexes = [self.ys.index(dot_y) for dot_y in vgate.get_dots_ys()]
            self.gates_dict[vgate.center_point[0]] = ToffoliGate(self.n_lines, target_line_coord, control_line_indexes)



class ToffoliGate:
    def __init__(self, n, target_line_index, control_lines_indexes=()):
        self.n_lines = n
        self.target_line_index = target_line_index
        self.control_lines_indexes = control_lines_indexes

    def set_control_lines_indexes(self):
        pass

    def set_target_line_index(self):
        pass