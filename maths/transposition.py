class Transposition:
    # можно инициализировать через массив результатов
    # можно инициализировать через упорядоченный массив гейтов
    def __init__(self, n, **kwargs):
        self.n = n
        self._generate_inputs(n)
        if 'outputs' in kwargs:
            self.outputs = kwargs['outputs']
        elif 'gates' in kwargs:  # gate - объект класса ToffoliGate из модуля circuit
            self.gates = kwargs['gates']
            self.outputs = []
            self._calculate_function()

    def _generate_inputs(self, n):
        self.inputs = []
        self.inputs_str = []
        for i in range(2 ** n):
            self.inputs.append(bin(i))
            self.inputs_str.append(str(bin(i))[2:].zfill(n))

    def _calculate_function(self):
        for input_str in self.inputs_str:
            self.outputs.append(self._calculate_function_for_input(input_str))
    
    def _calculate_function_for_input(self, input_str):
        output_str = input_str
        for gate in self.gates:
            if all(output_str[input_index] == '1' for input_index in gate.control_lines_indexes):
                changed_bit = '0' if output_str[gate.target_line_index] == '1' else '1'
                output_str = output_str[:gate.target_line_index] + changed_bit + output_str[gate.target_line_index + 1:]  
        return output_str


    def print_truth_table(self):
        for i in range(len(self.inputs_str)):
            print(' '.join(self.inputs_str[i]), '|', ' '.join(self.outputs[i]))

    
