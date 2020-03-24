from tkinter import *


class ToffoliGate(Frame):
	def __init__(self, canvas, n_controls, name, x=25, y=25, c=10):
		# n_controls - число управляющих линий
		self.n_controls = n_controls
		self.name_tag = name
		self.center_point = (x, y)
		self.c = c

		self.canvas = canvas
		self.create_gate(x, y)

	def create_gate(self, x, y):
		self.circle_id = self.canvas.create_oval(
			(x - self.c, y - self.c), (x + self.c, y + self.c), 
			outline="black", width=2, tags=(self.name_tag,)
		)
		self.horisontal_line_id = self.canvas.create_line(
			(x - self.c, y), (x + self.c, y), width=2, tags=(self.name_tag,)
		)
		self.vertical_line_id = self.canvas.create_line(
			(x, y - self.c), (x, y + 2 * self.n_controls * self.c), 
			width=2, tags=(self.name_tag,)
		)
		for i in range(self.n_controls):
			self.canvas.create_oval(
				(x - 3, y + (i + 1) * 2 * self.c - 3), 
				(x + 3, y + (i + 1) * 2 * self.c + 3), 
				fill="black", tags=(self.name_tag,)
			)

	def set_central_point(self, **kwargs):
		if 'x' in kwargs and 'y' in kwargs:
			self.center_point = (kwargs['x'], kwargs['y'])
			return
		if 'x_delta' in kwargs and 'y_delta' in kwargs:
			self.center_point = (
				self.center_point[0] + kwargs['x_delta'],
				self.center_point[1] + kwargs['y_delta']
			)
