from tkinter import *
from .toffoli_gate import ToffoliGate


c = 10  # constant for gate size

class mainFrame(Frame):
	def __init__(self, parent, width=400, height=400, lines_num=3):
		Frame.__init__(self, parent)
		self.parent = parent
		parent.geometry('%dx%d+%d+%d' % (800, 500, 400, 600))
		self.create_buttons(self.parent)

		self.canvas = Canvas(width=width, height=height, background="white")
		self.canvas.pack(expand=True)
		self.canvas.bind("<ButtonPress-1>", self.mouse_press)
		self.canvas.bind("<ButtonRelease-1>", self.mouse_release)
		self.canvas.bind("<B1-Motion>", self.drag_process)
		self.canvas.bind("<Button-2>", self.rotate_gate)  # клик колёсиком мыши
		
		self.gates = []
		self.nearest_gate_index = None
		self.current_mouse_position = None

		self.lines_ys = self.add_lines(lines_num)

	def addToffoliGate(self, n_controls, name="TofGate", x=25, y=25, up=True):
		self.gates.append(ToffoliGate(self.canvas, n_controls, name, x, y, up=up))

	def mouse_press(self, event):
		self.set_nearest_gate(event)
		if self.nearest_gate_index != None:
			self.current_mouse_position = (event.x, event.y)

	def mouse_release(self, event):
		if self.nearest_gate_index != None:
			nearest_line = self.get_nearest_line(event)
			if not nearest_line:
				self.nearest_gate.set_central_point(
					x_delta=event.x - self.current_mouse_position[0], 
					y_delta=event.y - self.current_mouse_position[1]
				)
			else:
				y_delta = nearest_line - self.nearest_gate.center_point[1]
				self.canvas.move(self.nearest_gate.name_tag, 0, y_delta)
				self.nearest_gate.set_central_point(x_delta=0, y_delta=y_delta)
		self.nearest_gate_index = None

	def drag_process(self, event):
		if self.nearest_gate_index:
			x_delta = event.x - self.current_mouse_position[0]
			y_delta = event.y - self.current_mouse_position[1]
			self.current_mouse_position = (event.x, event.y)
			self.canvas.move(self.nearest_gate.name_tag, x_delta, y_delta)
			self.nearest_gate.set_central_point(x_delta=x_delta, y_delta=y_delta)

	def rotate_gate(self, event):
		self.set_nearest_gate(event)
		if self.nearest_gate:
			params = (
				self.nearest_gate.n_controls,
				self.nearest_gate.name_tag,
				self.nearest_gate.center_point[0],
				self.nearest_gate.center_point[1],
				(not self.nearest_gate.up)
			)
			self.canvas.delete(self.nearest_gate.name_tag)
			self.gates[self.nearest_gate_index] = ToffoliGate(
				self.canvas,
				n_controls=params[0],
				name=params[1],
				x=params[2],
				y=params[3],
				up=params[4]
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
		for i in range(len(self.lines_ys) - self.nearest_gate.n_controls):
			delta_if_up = self.nearest_gate.center_point[1] - self.lines_ys[i]
			if self.nearest_gate.n_controls > 0:
				delta_if_down = self.nearest_gate.center_point[1] - 2 * self.nearest_gate.n_controls * self.nearest_gate.c  
			else:
				delta_if_down = self.nearest_gate.center_point[1] - self.nearest_gate.c
			delta_if_down -= self.lines_ys[i]

			if (self.nearest_gate.up and abs(delta_if_up) <= self.nearest_gate.c) or (not self.nearest_gate.up and abs(delta_if_down) <= self.nearest_gate.c):
				return self.lines_ys[i] if self.nearest_gate.up else self.lines_ys[i + self.nearest_gate.n_controls]
		return None

	def add_lines(self, n_lines):
		ys = []
		for i in range(n_lines):
			y = 200 + c * i * 2
			self.canvas.create_line(
				(0, y), (400, y),
				width=1, tags=("line" + str(i),) 
			)
			ys.append(y)
		return ys

	def create_buttons(self, parent):
		self.add0_button = Button(
			parent, text="add0", fg="black",
			command=lambda: self.addToffoliGate(0, name="TofGate0-" + str(len(self.gates) + 1))
		)
		self.add1_button = Button(
			parent, text="add1", fg="black",
			command=lambda: self.addToffoliGate(1, name="TofGate1-" + str(len(self.gates) + 1))
		)
		self.add2_button = Button(
			parent, text="add2", fg="black",
			command=lambda: self.addToffoliGate(2, name="TofGate2-" + str(len(self.gates) + 1))
		)
		self.add0_button.pack()
		self.add1_button.pack()
		self.add2_button.pack()

	def add(self):
		self.addToffoliGate(0, name="TofGate" + str(len(self.gates) + 1))
	
	def add1(self):
		self.addToffoliGate(1, name="TofGate" + str(len(self.gates) + 1))

	def add2(self):
		self.addToffoliGate(2, name="TofGate" + str(len(self.gates) + 1))

	@property
	def nearest_gate(self):
		if self.nearest_gate_index != None and self.nearest_gate_index < len(self.gates):
			return self.gates[self.nearest_gate_index]
		else:
			return None
	