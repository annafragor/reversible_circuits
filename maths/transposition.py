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
    
    def _calculate_function_for_input(self, input_str="", arr=None):
        if arr:
            input_str = ""
            for elem in arr:
                input_str += str(elem)
        output_str = input_str
        for gate in self.gates:
            if all(output_str[input_index] == '1' for input_index in gate.control_lines_indexes):
                changed_bit = '0' if output_str[gate.target_line_index] == '1' else '1'
                output_str = output_str[:gate.target_line_index] + changed_bit + output_str[gate.target_line_index + 1:]  
        return output_str
    
    def apply_gate(self, input_str="", input_arr=None, gate_index=-1, gate=None):
        if input_arr:
            input_str = ""
            for elem in input_arr:
                input_str += str(elem)
        output_str = input_str
        if self.gates or gate:
            if not gate:
                gate = self.gates[gate_index]
            if all(output_str[input_index] == '1' for input_index in gate.control_lines_indexes):
                changed_bit = '0' if output_str[gate.target_line_index] == '1' else '1'
                output_str = output_str[:gate.target_line_index] + changed_bit + output_str[gate.target_line_index + 1:]  
        return output_str

    def print_truth_table(self):
        for i in range(len(self.inputs_str)):
            print(' '.join(self.inputs_str[i]), '|', ' '.join(self.outputs_str[i]))
        print()

    def greedy_transform_algorythm(self, current_f_outputs=None):
        # straightforward Miller-Maslov algorythm
        self.gates = []  # circuit.ToffoliGate objects
        if not current_f_outputs:
            current_f_outputs = self.outputs_lst[:]
            outputs = self.outputs_lst[:]
        else:
            outputs = current_f_outputs[:]
        if current_f_outputs[0] != self.inputs_lst[0]:  # then we need to do Step1
            for l in range(self.n):
                if current_f_outputs[0][l] == 1:
                    self.gates.append(ToffoliGate(self.n, l))
                    for index in range(2 ** self.n):
                        r = [int(ch) for ch in self._calculate_function_for_input(arr=outputs[index])]
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
                            current_f_outputs[index] = [int(ch) for ch in self._calculate_function_for_input(arr=outputs[index])]
                    ind1_in_q = [m for m, e in enumerate(q) if e == 1]
                    ind1_in_i = [m for m, e in enumerate(self.inputs_lst[j]) if e == 1]
                    for ind1 in ind1_in_q:
                        self.gates.append(ToffoliGate(self.n, ind1, ind1_in_i))
                        for index in range(j, 2 ** self.n):
                            current_f_outputs[index] = [int(ch) for ch in self._calculate_function_for_input(arr=outputs[index])]
                    break

        self.gates.reverse()
    
    def input_to_output_transform_algorythm(self):
        sorted_inputs = self.inputs_lst[:]
        for i, output in enumerate(self.outputs_lst):
            sorted_inputs[self.inputs_lst.index(output)] = self.inputs_lst[i][:]
        self.greedy_transform_algorythm(current_f_outputs=sorted_inputs)
        self.gates.reverse()

    def input_to_output_transform_algorythm_(self):
        self.gates = []
        current_f_outputs = self.outputs_lst[:]
        table = [
            self.inputs_lst[:],  # inputs like [[0,0,0], [0,0,1], [0,1,0], ...]  
            self.outputs_lst[:]  # outputs
        ]
        
        if table[1].index(table[0][0]) != 0:  # f+(0) != 0 => invert inputs
            index = table[1].index(table[0][0])
            inp = table[0][index]  # such input that f(inp) = 0..0
            modified_inputs = self.inputs_lst[:]
            for l in range(self.n):
                if inp[l] == 1:
                    self.gates.append(ToffoliGate(self.n, l))
                    for index in range(2 ** self.n):
                        r = [int(ch) for ch in self._calculate_function_for_input(arr=modified_inputs[index])]
                        modified_inputs[index] = r
            self._update_table_with_swapped_inputs(table, modified_inputs)
        
        while not self._current_f_is_identical(table[1]):  
            for j in range(len(table[1])):   
                current_f_outputs = table[1]             
                if current_f_outputs[j] != self.inputs_lst[j]:                   
                    modified_inputs = table[0][:]
                    _f = self.inputs_lst[j][:]
                    _i =  self.inputs_lst[current_f_outputs.index(_f)][:]
                    p = [int(_f[l] < _i[l]) for l in range(self.n)]
                    q = [int(_f[l] > _i[l]) for l in range(self.n)]
                    ind1_in_p = [m for m, e in enumerate(p) if e == 1]
                    ind1_in_fi = [m for m, e in enumerate(_f) if e == 1]
                    for ind1 in ind1_in_p:
                        self.gates.append(ToffoliGate(self.n, ind1, ind1_in_fi))
                        for index in range(j, 2 ** self.n):
                            modified_inputs[index] = [int(ch) for ch in self.apply_gate(input_arr=modified_inputs[index])]
                    ind1_in_q = [m for m, e in enumerate(q) if e == 1]
                    ind1_in_i = [m for m, e in enumerate(_i) if e == 1]
                    for ind1 in ind1_in_q:
                        self.gates.append(ToffoliGate(self.n, ind1, ind1_in_i))
                        for index in range(j, 2 ** self.n):
                            modified_inputs[index] = [int(ch) for ch in self.apply_gate(input_arr=modified_inputs[index])]
                    self._update_table_with_swapped_inputs(table, modified_inputs)
                    break

    def _update_table_with_swapped_inputs(self, table, modified_inputs):
        swapped_outputs = [0 for i in range(2 ** self.n)]
        for new_inp_index in range(2 ** self.n):
            swapped_outputs[new_inp_index] = table[1][self.inputs_lst.index(modified_inputs[new_inp_index])]
        table[1] = swapped_outputs

    def bidirectional_transform(self):
        # miller-maslov bidirectional algorythm
        self.gates = []
        table = [
            self.inputs_lst[:],  # inputs like [[0,0,0], [0,0,1], [0,1,0], ...]  
            self.outputs_lst[:]  # outputs
        ]
        left_gates = []
        right_gates = []
        print("111")
        
        if table[1].index(table[0][0]) != 0:  # f+(0) != 0 => invert inputs
            inp_out_delta = self.hamming_distance(table[1][0], table[0][0])
            index = table[1].index(table[0][0])
            inp = table[0][index]  # such input that f(inp) = 0..0
            inp_inp_delta = self.hamming_distance(table[0][0], inp)
            modified_inputs = self.inputs_lst[:]
            if inp_out_delta <= inp_inp_delta:
                # do output-to-input algo
                for l in range(self.n):
                    if table[1][0][l] == 1:
                        right_gates.append(ToffoliGate(self.n, l))
                        for index in range(2 ** self.n):
                            r = [int(ch) for ch in self._calculate_function_for_input(arr=table[1][index])]
                            table[1][index] = r
            else:
                # do input-to-output algo
                for l in range(self.n):
                    if inp[l] == 1:
                        left_gates.append(ToffoliGate(self.n, l))
                        for index in range(2 ** self.n):
                            r = [int(ch) for ch in self.apply_gate(input_arr=modified_inputs[index], gate=left_gates[-1])]
                            modified_inputs[index] = r
                self._update_table_with_swapped_inputs(table, modified_inputs)

        while not self._current_f_is_identical(table[1]):  
            for j in range(len(table[1])):   
                if table[1][j] != self.inputs_lst[j]:     
                    inp_out_delta = self.hamming_distance(table[1][j], self.inputs_lst[j])              
                    modified_inputs = table[0][:]
                    _f = self.inputs_lst[j][:]
                    _i =  self.inputs_lst[table[1].index(_f)][:]
                    inp_inp_delta = self.hamming_distance(_f, _i)
                    if inp_out_delta <= inp_inp_delta:
                        # do output-to-input algo
                        p = [int(table[1][j][l] < self.inputs_lst[j][l]) for l in range(self.n)]
                        q = [int(table[1][j][l] > self.inputs_lst[j][l]) for l in range(self.n)]
                        ind1_in_p = [m for m, e in enumerate(p) if e == 1]
                        ind1_in_fi = [m for m, e in enumerate(table[1][j]) if e == 1]
                        for ind1 in ind1_in_p:
                            right_gates.append(ToffoliGate(self.n, ind1, ind1_in_fi))
                            for index in range(j, 2 ** self.n):
                                table[1][index] = [int(ch) for ch in self.apply_gate(input_arr=table[1][index], gate=right_gates[-1])]
                        ind1_in_q = [m for m, e in enumerate(q) if e == 1]
                        ind1_in_i = [m for m, e in enumerate(self.inputs_lst[j]) if e == 1]
                        for ind1 in ind1_in_q:
                            right_gates.append(ToffoliGate(self.n, ind1, ind1_in_i))
                            for index in range(j, 2 ** self.n):
                                table[1][index] = [int(ch) for ch in self.apply_gate(input_arr=table[1][index], gate=right_gates[-1])]
                    else:
                        # do input-to-output algo
                        p = [int(_f[l] < _i[l]) for l in range(self.n)]
                        q = [int(_f[l] > _i[l]) for l in range(self.n)]
                        ind1_in_p = [m for m, e in enumerate(p) if e == 1]
                        ind1_in_fi = [m for m, e in enumerate(_f) if e == 1]
                        for ind1 in ind1_in_p:
                            left_gates.append(ToffoliGate(self.n, ind1, ind1_in_fi))
                            for index in range(j, 2 ** self.n):
                                modified_inputs[index] = [int(ch) for ch in self.apply_gate(input_arr=modified_inputs[index], gate=left_gates[-1])]
                        ind1_in_q = [m for m, e in enumerate(q) if e == 1]
                        ind1_in_i = [m for m, e in enumerate(_i) if e == 1]
                        for ind1 in ind1_in_q:
                            left_gates.append(ToffoliGate(self.n, ind1, ind1_in_i))
                            for index in range(j, 2 ** self.n):
                                modified_inputs[index] = [int(ch) for ch in self.apply_gate(input_arr=modified_inputs[index], gate=left_gates[-1])]
                        self._update_table_with_swapped_inputs(table, modified_inputs)
                    break
        right_gates.reverse()
        self.gates = left_gates + right_gates
       

    def hamming_distance(self, str1, str2):
        distance = 0
        if len(str1) != len(str2):
            return -1
        for i in range(len(str1)):
            if str1[i] != str2[i]:
                distance += 1
        return distance

    def _current_f_is_identical(self, current_outputs=()):
        return all(current_outputs[j] == self.inputs_lst[j] for j in range(2 ** self.n))
