from .circuit import ToffoliGate


class Transposition:
    # можно инициализировать через массив результатов
    # можно инициализировать через упорядоченный массив гейтов
    def __init__(self, n, **kwargs):
        self.n = n
        self._generate_inputs(n)
        self.gates = []
        self.outputs_str = []
        self.outputs_lst = []
        if 'outputs' in kwargs:
            for output in kwargs['outputs']:
                self.outputs_str.append(str(bin(output))[2:].zfill(n))
                self.outputs_lst.append([int(ch) for ch in self.outputs_str[-1]])
        elif 'gates' in kwargs:  # gate - объект класса ToffoliGate из модуля circuit
            self.gates = kwargs['gates']
            self._calculate_function()
        elif 'circuit' in kwargs:
            circuit = kwargs['circuit']
            for coord in sorted(circuit.gates_dict):
                gate = circuit.gates_dict[coord]
                self.gates.append(gate)
            self._calculate_function()

    def _generate_inputs(self, n):
        self.inputs_lst = []
        self.inputs_str = []
        for i in range(2 ** n):
            self.inputs_str.append(str(bin(i))[2:].zfill(n))
            self.inputs_lst.append([int(ch) for ch in self.inputs_str[-1]])

    def _calculate_function(self):
        for input_str in self.inputs_str:
            self.outputs_str.append(self._calculate_function_for_input(input_str))
    
    def _calculate_function_for_input(self, input_str):
        output_str = input_str
        for gate in self.gates:
            if all(output_str[input_index] == '1' for input_index in gate.control_lines_indexes):
                changed_bit = '0' if output_str[gate.target_line_index] == '1' else '1'
                output_str = output_str[:gate.target_line_index] + changed_bit + output_str[gate.target_line_index + 1:]  
        return output_str

    def print_truth_table(self):
        for i in range(len(self.inputs_str)):
            print(' '.join(self.inputs_str[i]), '|', ' '.join(self.outputs_str[i]))
        print()

    def greedy_transform_algorythm(self):
        # straightforward Miller-Maslov algorythm
        self.gates = []  # circuit.ToffoliGate objects
        current_f_outputs = self.outputs_lst[:]
        if current_f_outputs[0] != self.inputs_lst[0]:  # then we need to do Step1
            for l in range(self.n):
                if current_f_outputs[0][l] == 1:
                    self.gates.append(ToffoliGate(self.n, l))
                    for index in range(2 ** self.n):
                        r = [int(ch) for ch in self._calculate_function_for_input(self.outputs_str[index])]
                        current_f_outputs[index] = r

        while not self._current_f_is_identical(current_f_outputs):  # cyclic call of Step2
            for j in range(len(current_f_outputs)):
                if current_f_outputs[j] != self.inputs_lst[j]:
                    p = [int(current_f_outputs[j][l] < self.inputs_lst[j][l]) for l in range(self.n)]
                    q = [int(current_f_outputs[j][l] > self.inputs_lst[j][l]) for l in range(self.n)]
                    ind1_in_p = [m for m, e in enumerate(p) if e == 1]
                    ind1_in_fi = [m for m, e in enumerate(current_f_outputs[j]) if e == 1]
                    for ind1 in ind1_in_p:
                        self.gates.append(ToffoliGate(self.n, ind1, ind1_in_fi))
                        for index in range(j, 2 ** self.n):
                            current_f_outputs[index] = [int(ch) for ch in self._calculate_function_for_input(self.outputs_str[index])]
                    ind1_in_q = [m for m, e in enumerate(q) if e == 1]
                    ind1_in_i = [m for m, e in enumerate(self.inputs_lst[j]) if e == 1]
                    for ind1 in ind1_in_q:
                        self.gates.append(ToffoliGate(self.n, ind1, ind1_in_i))
                        for index in range(j, 2 ** self.n):
                            current_f_outputs[index] = [int(ch) for ch in self._calculate_function_for_input(self.outputs_str[index])]
                    break

        self.gates.reverse()
    
    def _current_f_is_identical(self, current_outputs):
        return all(current_outputs[j] == self.inputs_lst[j] for j in range(2 ** self.n))
