from tkinter import *
from .toffoli_gate import ToffoliGateVisual
from maths.circuit import Circuit
from maths.transposition import Transposition

c = 10  # constant for gate size


class mainFrame(Frame):
	def __init__(self, parent, width=600, height=300, lines_num=3):
		Frame.__init__(self, parent)
		self.parent = parent
		parent.geometry('%dx%d' % (800, 500))
		self.selected_control_lines_indexes = []
		self.checkboxes_for_control_lines = []
		self.gates = []
		self.gates_indexes_on_lines = []
		self.nearest_gate_index, self.current_mouse_position = None, None
		self.circuit = None

		self._set_up_canvas(width, height, lines_num)	

	def _set_up_canvas(self, width, height, lines_num):
		self.canvas = Canvas(width=width, height=height, background="white")
		self.canvas.pack(expand=True)
		self.canvas.bind("<ButtonPress-1>", self.mouse_press)
		self.canvas.bind("<ButtonRelease-1>", self.mouse_release)
		self.canvas.bind("<B1-Motion>", self.drag_process)
		self.canvas.bind("<Button-2>", self.rotate_gate)  # клик колёсиком мыши
		self._add_lines(lines_num, width)
		self._create_buttons()

	def mouse_press(self, event):
		self.set_nearest_gate(event)
		if self.nearest_gate_index != None:
			self.current_mouse_position = (event.x, event.y)

	def mouse_release(self, event):
		if self.nearest_gate_index != None:
			nearest_line = self.get_nearest_line(event)
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
		if do:
			# примагничиваем элемент к проводу
			# добавляем его в список элементов, которые находятся именно на обратимой схеме (т.е. на проводах)
			y_delta = nearest_line - self.nearest_gate.center_point[1]
			self.canvas.move(self.nearest_gate.name_tag, 0, y_delta)
			self.nearest_gate.reset_coordinates(x_delta=0, y_delta=y_delta)
			if not self.nearest_gate.on_schema:  # если элемент не был на схеме (если был - ничего делать не нужно)
				self.nearest_gate.on_schema = True
				self.gates_indexes_on_lines.append(self.nearest_gate_index)
		else:
			# отрисовываем элемент там, где отжали кнопку, не добавляя на схему
			self.nearest_gate.reset_coordinates(
				x_delta=event.x - self.current_mouse_position[0], 
				y_delta=event.y - self.current_mouse_position[1]
			)
			# проверка, не был ли этот элемент удалён с самой схемы
			if self.nearest_gate.on_schema:
				# если да - удаление из индексов
				self.gates_indexes_on_lines.remove(self.nearest_gate_index)
				self.nearest_gate.on_schema = False
		self.nearest_gate_index = None

	def drag_process(self, event):
		if self.nearest_gate_index:
			x_delta = event.x - self.current_mouse_position[0]
			y_delta = event.y - self.current_mouse_position[1]
			self.current_mouse_position = (event.x, event.y)
			self.canvas.move(self.nearest_gate.name_tag, x_delta, y_delta)
			self.nearest_gate.reset_coordinates(x_delta=x_delta, y_delta=y_delta)

	def rotate_gate(self, event):
		self.set_nearest_gate(event)
		if self.nearest_gate:
			params = (
				self.nearest_gate.name_tag,
				self.nearest_gate.target_index,
				self.nearest_gate.control_indexes,
				self.nearest_gate.center_point[0],
				self.nearest_gate.center_point[1],
				(not self.nearest_gate.up)
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
				up=params[5]
            )			

	def set_nearest_gate(self, event):
		for i in range(len(self.gates)):
			gate = self.gates[i]
			if abs(gate.center_point[0] - event.x) <= c and abs(gate.center_point[1] - event.y) <= c:
				self.nearest_gate_index = i
				break

	def get_nearest_line(self, event):
		if self.nearest_gate.n_controls >= len(self.lines_ys):
			return None		
		for i in range(len(self.lines_ys)):
			delta_if_up = self.nearest_gate.center_point[1] - self.lines_ys[i]
			if self.nearest_gate.n_controls > 0:
				delta_if_down = self.nearest_gate.center_point[1] - 2 * self.nearest_gate.n_controls * self.nearest_gate.c  
			else:
				delta_if_down = self.nearest_gate.center_point[1] - self.nearest_gate.c
			delta_if_down -= self.lines_ys[i]

			if (self.nearest_gate.up and abs(delta_if_up) <= self.nearest_gate.c) or (not self.nearest_gate.up and abs(delta_if_down) <= self.nearest_gate.c):
				return self.lines_ys[i] if self.nearest_gate.up else self.lines_ys[i + self.nearest_gate.n_controls]
		return None

	def _add_lines(self, n_lines, width):
		self.lines_ys = []
		for i in range(n_lines):
			y = 200 + c * i * 2
			self.canvas.create_line(
				(0, y), (width, y),
				width=1, tags=("line" + str(i),) 
			)
			self.lines_ys.append(y)
			self.canvas.create_text(10, y - 5, text="x"+str(n_lines - i - 1))
			self.canvas.create_text(width - 5, y - 5, text="y"+str(n_lines - i - 1))

	def add_gate(self):
		print("control", [var.get() for var in self.selected_control_lines_indexes])
		print("target", self.selected_target_index.get())
		name = "TofGate" + str(len(self.gates) + 1)
		control_indexes = [var.get() for var in self.selected_control_lines_indexes]
		self.gates.append(ToffoliGateVisual(
			self.canvas, 
			n=len(self.lines_ys),
			target_index=self.selected_target_index.get(), 
			selected_control_indexes=[i for i, e in enumerate(control_indexes) if e == 1],
			name=name
			)
		)

	def _create_buttons(self):
		self.add_button = Button(
			self.parent, text="+", fg="black",
			command=self.add_gate
		)
		self.add_button.pack()
		
		for i in range(len(self.lines_ys)):
			self.selected_control_lines_indexes.append(IntVar())
			self.checkboxes_for_control_lines.append(Checkbutton(
				self.parent, 
				text=str(i), 
				variable=self.selected_control_lines_indexes[i],
				state=NORMAL if i > 0 else DISABLED
				)
			)
			self.checkboxes_for_control_lines[i].pack()
		
		self.selected_target_index = IntVar()
		self.selected_target_index.set(0)
		for i in range(len(self.lines_ys)):
			Radiobutton(text=str(i), variable=self.selected_target_index, value=i, command=self.disable_checkbox).pack()
		
		self.calculate_transposition_button = Button(
			self.parent, text="calculate transposition", fg="black",
			command=self.calculate_transposition
		)
		self.calculate_transposition_button.pack()

	def disable_checkbox(self):
		for i, checkbox in enumerate(self.checkboxes_for_control_lines):
			if i != self.selected_target_index.get():
				checkbox.config(state=NORMAL)
			else:
				self.selected_control_lines_indexes[i].set(0)
				checkbox.config(state=DISABLED)

	def calculate_transposition(self):
		gates = [self.gates[index] for index in self.gates_indexes_on_lines]
		n = len(self.lines_ys)
		self.circuit = Circuit(n, visual_gates=gates, y_lines=self.lines_ys)
		tr = Transposition(n, circuit=self.circuit)
		tr.print_truth_table()

	@property
	def nearest_gate(self):
		if self.nearest_gate_index != None and self.nearest_gate_index < len(self.gates):
			return self.gates[self.nearest_gate_index]
		else:
			return None
	