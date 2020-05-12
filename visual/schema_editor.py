from tkinter import *
from .toffoli_gate import ToffoliGateVisual
from maths.circuit import Circuit
from maths.transposition import Transposition
from numpy.random import permutation
import re

c = 10  # constant for gate size


class EditorFrame:
	def __init__(self, parent_window, parent_size, lines_num=3):
		self.parent_window = parent_window
		self.root = Toplevel(parent_window.root)
		w, h = parent_size[0], parent_size[1]
		self.root.geometry("550x400+{}+{}".format(250+w, h)) 
		self.root.title("Схема")
		# self.root.resizable(False, False)

		self.selected_control_lines_indexes = []
		self.checkboxes_for_control_lines = []
		self.gates = []
		self.test_gate = None
		self.gates_indexes_on_lines = []
		self.nearest_gate_index, self.current_mouse_position = None, None
		self.circuit = None

		self._set_up_window(120 * int(lines_num), 70 * int(lines_num), int(lines_num))

	def _set_up_window(self, width, height, lines_num):
		gridframe_left = Frame(self.root)
		gridframe_right = Frame(self.root)
		gridframe_add = Frame(gridframe_left)
		self._set_up_canvas(gridframe_left, width, height, lines_num)	
		self._create_add_buttons(gridframe_add)
		self._create_algo_buttons(gridframe_right)
		self._create_other(gridframe_left)
		gridframe_add.grid(row=0, column=0)
		gridframe_left.grid(row=0, column=0)
		gridframe_right.grid(row=0, column=1)

	def on_horizontal(self, event):
		self.canvas.xview_scroll(-1 * event.delta, 'units')
	
	def _set_up_canvas(self, gridframe, width, height, lines_num):
		self.canvas = Canvas(gridframe, width=width, height=height, background="white", scrollregion=(0, 0, width * 3, width * 3))
		self.canvas.grid(row=1, column=0)
		hbar = Scrollbar(gridframe, orient=HORIZONTAL)
		hbar.grid(row=2, column=0)
		hbar.config(command=self.canvas.xview)
		self.canvas.config(xscrollcommand=hbar.set)
		self.canvas.bind("<ButtonPress-1>", self.mouse_press)
		self.canvas.bind("<ButtonRelease-1>", self.mouse_release)
		self.canvas.bind("<B1-Motion>", self.drag_process)
		self.canvas.bind("<Button-2>", self.rotate_gate)  # клик колёсиком мыши
		self.canvas.bind('<Shift-MouseWheel>', self.on_horizontal)
		self._add_lines(lines_num, width)

	def extended_event(self, event):
		return (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))

	def mouse_press(self, event):
		event = self.extended_event(event)
		self.set_nearest_gate(event)
		if self.nearest_gate_index != None:
			self.current_mouse_position = event

	def mouse_release(self, event):
		event = self.extended_event(event)
		self.set_nearest_gate(event)
		if self.nearest_gate_index != None:
			nearest_line = self.get_nearest_line()
			dots_ys = self.nearest_gate.get_dots_ys()
			if nearest_line: 
				if dots_ys:
					min_dot_y = min(dots_ys)
					max_dot_y = max(dots_ys)
					if (self.lines_ys[0] - min_dot_y < self.nearest_gate.c) and (max_dot_y - self.lines_ys[-1] < self.nearest_gate.c):
						self.magnet(nearest_line, event, do=True)
						return
				else:
					self.magnet(nearest_line, event, do=True)
					return
			self.magnet(nearest_line, event, do=False)
	
	def magnet(self, nearest_line, event, do=True):
		if self.truth_table.get():
			msg = "Data in the truth table is not valid anymore."
		else:
			msg = ""
		if do:
			# примагничиваем элемент к проводу
			# добавляем его в список элементов, которые находятся именно на обратимой схеме (т.е. на проводах)
			y_delta = nearest_line - self.nearest_gate.center_point[1]
			self.canvas.move(self.nearest_gate.name_tag, 0, y_delta)
			self.nearest_gate.reset_coordinates(x_delta=0, y_delta=y_delta)
			if not self.nearest_gate.on_schema:  # если элемент не был на схеме (если был - ничего делать не нужно)
				self.nearest_gate.on_schema = True
				self.gates_indexes_on_lines.append(self.nearest_gate_index)
				self.info_text.set("INFO: You added gate to the circuit.\n" + msg)
			elif y_delta:  # если элемент был на схеме, но переместился на другой провод
				self.info_text.set("INFO: You moved gate on the circuit.\n" + msg)
		else:
			# отрисовываем элемент там, где отжали кнопку, не добавляя на схему
			self.nearest_gate.reset_coordinates(
				x_delta=event[0] - self.current_mouse_position[0], 
				y_delta=event[1] - self.current_mouse_position[1]
			)
			# проверка, не был ли этот элемент удалён с самой схемы
			if self.nearest_gate.on_schema:
				# если да - удаление из индексов
				self.gates_indexes_on_lines.remove(self.nearest_gate_index)
				self.nearest_gate.on_schema = False

				self.info_text.set("INFO: You removed gate from the circuit.\n" + msg)
		self.nearest_gate_index = None

	def drag_process(self, event):
		event = self.extended_event(event)
		if self.nearest_gate_index is not None:
			x_delta = event[0] - self.current_mouse_position[0]
			y_delta = event[1] - self.current_mouse_position[1]
			self.current_mouse_position = event
			self.canvas.move(self.nearest_gate.name_tag, x_delta, y_delta)
			self.nearest_gate.reset_coordinates(x_delta=x_delta, y_delta=y_delta)

	def rotate_gate(self, event):
		self.set_nearest_gate(self.extended_event(event))
		if self.nearest_gate:
			params = (
				self.nearest_gate.name_tag,
				len(self.lines_ys) - self.nearest_gate.target_index - 1,
				[len(self.lines_ys) - index - 1 for index in self.nearest_gate.control_indexes],
				self.nearest_gate.center_point[0],
				self.nearest_gate.center_point[1] + 2,
			)
			self.canvas.delete(self.nearest_gate.name_tag)
			self.gates[self.nearest_gate_index] = ToffoliGateVisual(
				self.canvas,
				len(self.lines_ys),
				name=params[0],
				target_index=params[1],
				selected_control_indexes=params[2],
				x=params[3],
				y=params[4],
            )			

	def set_nearest_gate(self, event):
		for i in range(len(self.gates)):
			gate = self.gates[i]
			if abs(gate.center_point[0] - event[0]) <= c and abs(gate.center_point[1] - event[1]) <= c:
				self.nearest_gate_index = i
				break

	def get_nearest_line(self):
		if self.nearest_gate.n_controls >= len(self.lines_ys):
			return None		
		for i in range(len(self.lines_ys)):
			if self.nearest_gate.center_point[1] >= self.lines_ys[i]:  # центр ниже текущей линии, т.е. нужно проверить, поднимаем ли элемент выше
				delta = self.nearest_gate.center_point[1] - self.lines_ys[i]
			else:  # центр выше текущей линии, т.е. нужно проверить, опускаем ли элемент ниже
				delta = self.lines_ys[i] - self.nearest_gate.center_point[1]
			if delta <= self.nearest_gate.c:
					return self.lines_ys[i]
		return None

	def _add_lines(self, n_lines, width):
		self.lines_ys = []
		for i in range(n_lines):
			y = width / 2 - n_lines * c + c * i * 2
			self.canvas.create_line(
				(0, y), (width * 3, y),
				width=1, tags=("line" + str(i),) 
			)
			self.lines_ys.append(y)
			self.canvas.create_text(10, y - 5, text="x"+str(n_lines - i - 1))
			self.canvas.create_text(width - 5, y - 5, text="y"+str(n_lines - i - 1))

	def add_gate(self, test=False):
		name = "TofGate" + str(len(self.gates) + 1)
		control_indexes = [var.get() for var in self.selected_control_lines_indexes]
		gate = ToffoliGateVisual(
			self.canvas if not test else self.test_canvas, 
			n=len(self.lines_ys),
			target_index=self.selected_target_index.get(), 
			selected_control_indexes=[i for i, e in enumerate(control_indexes) if e == 1],
			name=name,
			on_schema=False,
			x=20 if test else 50,
			y=15 + 20 * self.selected_target_index.get() if test else 50
		)
		if not test:
			self.gates.append(gate)
		else:
			self.test_gate = gate

	def draw_schema_from_input(self, straight=False, backward=False, bidirectional=False):
		input_func_list = [int(inp) for inp in re.findall(r"(\d+)\.{0,1}", self.input_func_int_data.get())]
		if len(input_func_list) != 2 ** len(self.lines_ys) or len(set(input_func_list)) != 2 ** len(self.lines_ys):
			return
		tr = Transposition(len(self.lines_ys), outputs=input_func_list)
		if straight:
			tr.greedy_transform_algorythm()
		elif backward:
			tr.input_to_output_transform_algorythm()
		else:
			tr.bidirectional_transform()  # by default do straightforward
		self.draw_schema_from_math_gates(tr.gates)

	def draw_schema_from_math_gates(self, gates):
		self.clear_canvas()
		for i, gate in enumerate(gates):
			self.gates.append(ToffoliGateVisual(
				self.canvas, 
				n=len(self.lines_ys),
				target_index=-gate.target_line_index - 1, 
				selected_control_indexes=[-index - 1 for index in gate.control_lines_indexes],
				name="TofGateMillerMaslov" + str(i),
				x=30 * (i + 1), 
				y=self.lines_ys[-gate.target_line_index - 1], 
				on_schema=True
				)
			)
			self.gates_indexes_on_lines.append(i)

	def clear_canvas(self):
		for gate in self.gates:
			self._remove_gate_from_canvas(gate, self.canvas)
		self.gates = []
		self.gates_indexes_on_lines = []

	def _remove_gate_from_canvas(self, gate, canvas):
		canvas.delete(gate.circle_id)
		canvas.delete(gate.horisontal_line_id)
		canvas.delete(gate.vertical_line_id)
		for dot_id in gate.dots_id:
			canvas.delete(dot_id)

	def _create_add_buttons(self, gridframe):
		inner_gridframe = Frame(gridframe)
		inner_gridframe.grid(row=0, column=0)
		
		for i in range(len(self.lines_ys)):
			self.selected_control_lines_indexes.append(IntVar())
			self.checkboxes_for_control_lines.append(Checkbutton(
				inner_gridframe, 
				text=str(i), 
				variable=self.selected_control_lines_indexes[i],
				state=NORMAL if i > 0 else DISABLED,
				command=self._preview_gate
				)
			)
			self.checkboxes_for_control_lines[i].grid(row=i, column=0)
		
		self.selected_target_index = IntVar()
		self.selected_target_index.set(0)
		for i in range(len(self.lines_ys)):
			r = Radiobutton(inner_gridframe, text=str(i), variable=self.selected_target_index, value=i, command=self.disable_checkbox)
			r.grid(row=i, column=1)

		self.test_canvas = Canvas(gridframe, width=40, height=len(self.lines_ys) * 20 + 10, background="white")
		self.test_canvas.grid(row=0, column=1)

		self.add_button = Button(
			gridframe, text="add gate", fg="black",
			command=self.add_gate
		)
		self.add_button.grid(row=0, column=3)
		self._preview_gate()

	def _create_algo_buttons(self, gridframe):
		self.generate_random_btn = Button(
			gridframe, text="generate random", fg="black",
			command=self._generate_random_input,
		)
		self.generate_random_btn.grid(row=0, column=0)

		label = Label(gridframe, text="input function")
		label.grid(row=1, column=0)

		self.input_func_int_data = Entry(
			gridframe, validate="key"
		)
		self.input_func_int_data['validatecommand'] = (self.input_func_int_data.register(self._check_input),'%P','%d')
		self.input_func_int_data.grid(row=2, column=0)
		
		self.truth_table = StringVar()
		tr_t = Message(gridframe, textvariable=self.truth_table)
		tr_t.grid(row=3, column=0)
		
		self.backward_algo_btn = Button(
			gridframe, text="backward algo", fg="black",
			command=lambda: self.draw_schema_from_input(straight=True),
			state=DISABLED
		)
		self.backward_algo_btn.grid(row=4, column=0)

		self.straightforward_algo_btn = Button(
			gridframe, text="straightforward algo", fg="black",
			command=lambda: self.draw_schema_from_input(backward=True),
			state=DISABLED
		)
		self.straightforward_algo_btn.grid(row=5, column=0)

		self.bidirection_algo_btn = Button(
			gridframe, text="bidirectional algo", fg="black",
			command=lambda: self.draw_schema_from_input(bidirectional=True),
			state=DISABLED
		)
		self.bidirection_algo_btn.grid(row=6, column=0)

	def _create_other(self, gridframe):
		inner_gridframe = Frame(gridframe)
		inner_gridframe.grid(row=3, column=0)
		self.calculate_transposition_button = Button(
			inner_gridframe, text="calculate transposition", fg="black",
			command=self.calculate_transposition
		)
		self.calculate_transposition_button.grid(row=0, column=0)

		self.clear_btn = Button(
			inner_gridframe, text="clear canvas", fg="black",
			command=self.clear_canvas
		)
		self.clear_btn.grid(row=0, column=1)

		self.error_text = StringVar()
		err_t = Message(gridframe, textvariable=self.error_text, width=300)
		err_t.grid(row=4)

		self.info_text = StringVar()
		info_t = Message(gridframe, textvariable=self.info_text, width=300)
		info_t.grid(row=5)

	def _generate_random_input(self):
		generated_input = ".".join([str(elem) for elem in permutation(2 ** len(self.lines_ys))])
		if self.input_func_int_data.get():
			self.input_func_int_data.delete(0, END)
		self.input_func_int_data.insert(0, generated_input)

	def disable_checkbox(self):
		for i, checkbox in enumerate(self.checkboxes_for_control_lines):
			if i != self.selected_target_index.get():
				checkbox.config(state=NORMAL)
			else:
				self.selected_control_lines_indexes[i].set(0)
				checkbox.config(state=DISABLED)
		self._preview_gate()

	def _preview_gate(self):
		if self.test_gate:
			self._remove_gate_from_canvas(self.test_gate, self.test_canvas)
		self.add_gate(test=True)

	def calculate_transposition(self):
		self.gates_indexes_on_lines = [i for i, gate in enumerate(self.gates) if gate.on_schema]
		gates = [self.gates[index] for index in self.gates_indexes_on_lines]
		self.info_text.set("")
		if not gates:
			self.info_text.set("INFO: You have no gates on schema. Your transposition is identity.")
		n = len(self.lines_ys)
		self.circuit = Circuit(n, visual_gates=gates, y_lines=self.lines_ys)
		tr = Transposition(n, circuit=self.circuit)
		self.truth_table.set(tr.get_truth_table())

	@property
	def nearest_gate(self):
		if self.nearest_gate_index != None and self.nearest_gate_index < len(self.gates):
			return self.gates[self.nearest_gate_index]
		else:
			return None

	def _check_input(self, inp_str, acttyp):
		if acttyp == '1': # 1 = insert, 0 = delete, -1 = others
			if not re.fullmatch(r"((\d+)\.{0,1})*", inp_str):
				return False
		input_func_list = [int(inp) for inp in re.findall(r"(\d+)\.{0,1}", inp_str)]
		if set(input_func_list) != set(list(range(2 ** len(self.lines_ys)))):
			self.straightforward_algo_btn['state'] = DISABLED
			self.backward_algo_btn['state'] = DISABLED
			self.bidirection_algo_btn['state'] = DISABLED
			if input_func_list:
				self.error_text.set("ERROR: Invalid input function data.")
			else:
				self.error_text.set("")
		else:
			self.straightforward_algo_btn['state'] = NORMAL
			self.backward_algo_btn['state'] = NORMAL
			self.bidirection_algo_btn['state'] = NORMAL
			self.error_text.set("")
		return True
