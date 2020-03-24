from tkinter import *
from .toffoli_gate import ToffoliGate


c = 10  # constant for gate size


class mainFrame(Frame):
	def __init__(self, parent, width=400, height=400, lines_num=3):
		Frame.__init__(self, parent)
		parent.geometry('%dx%d+%d+%d' % (800, 500, 400, 600))

		self.canvas = Canvas(width=width, height=height, background="white")
		self.canvas.pack(expand=True)
		self.canvas.bind("<ButtonPress-1>", self.mouse_press)
		self.canvas.bind("<ButtonRelease-1>", self.mouse_release)
		self.canvas.bind("<B1-Motion>", self.drag_process)
		self.gates = []
		self.nearest_gate = None
		self.current_mouse_position = None

		self.lines_ys = self.add_lines(lines_num)

	def addToffoliGate(self, n_controls, name="TofGate", x=25, y=25):
		self.gates.append(ToffoliGate(self.canvas, n_controls, name, x, y))

	def mouse_press(self, event):
		self.set_nearest_gate(event)
		if self.nearest_gate:
			self.current_mouse_position = (event.x, event.y)

	def mouse_release(self, event):
		if self.nearest_gate:
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
		self.nearest_gate = None

	def drag_process(self, event):
		if self.nearest_gate:
			x_delta = event.x - self.current_mouse_position[0]
			y_delta = event.y - self.current_mouse_position[1]
			self.current_mouse_position = (event.x, event.y)
			self.canvas.move(self.nearest_gate.name_tag, x_delta, y_delta)
			self.nearest_gate.set_central_point(x_delta=x_delta, y_delta=y_delta)

	def set_nearest_gate(self, event):
		for gate in self.gates:
			if abs(gate.center_point[0] - event.x) <= c and abs(gate.center_point[1] - event.y) <= c:
				self.nearest_gate = gate
				break

	def get_nearest_line(self, event):
		if self.nearest_gate.n_controls >= len(self.lines_ys):
			return None
		for i in range(len(self.lines_ys) - self.nearest_gate.n_controls):
			if abs(self.nearest_gate.center_point[1] - self.lines_ys[i]) <= c:
				return self.lines_ys[i]
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