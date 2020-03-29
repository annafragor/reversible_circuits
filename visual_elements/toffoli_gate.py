from tkinter import Frame


class ToffoliGateVisual(Frame):
	def __init__(self, canvas, n, target_index, selected_control_indexes, name, x=50, y=50, c=10, up=True, on_schema=False):
		# n_controls - число управляющих линий
		self.n_controls = len(selected_control_indexes)
		self.name_tag = name
		self.center_point = (x, y)
		self.c = c
		self.up = up
		self.on_schema = on_schema
		self.target_index = target_index
		self.control_indexes = selected_control_indexes

		self.canvas = canvas
		self._create_gate(x, y)

	def _create_gate(self, x, y):
		self.circle_id = self.canvas.create_oval(
			(x - self.c, y - self.c), (x + self.c, y + self.c), 
			outline="black", width=2, tags=(self.name_tag,)
		)
		self.horisontal_line_id = self.canvas.create_line(
			(x - self.c, y), (x + self.c, y), width=2, tags=(self.name_tag,)
		)
        
		ys_vertical = [y - self.c, y + self.c]
		if self.n_controls > 0:
			min_control_index = min(self.control_indexes)
			max_control_index = max(self.control_indexes)

			if min_control_index < self.target_index:
				if self.up:
					ys_vertical[0] = y - 2 * self.c * (self.target_index - min_control_index)
				else:
					ys_vertical[1] = y + 2 * self.c * (self.target_index - min_control_index)
			if max_control_index > self.target_index:
				if self.up:
					ys_vertical[1] = y + 2 * self.c * (max_control_index - self.target_index)
				else:
					ys_vertical[0] = y - 2 * self.c * (max_control_index - self.target_index)
		
		self.vertical_line_id = self.canvas.create_line(
			(x, ys_vertical[0]), (x, ys_vertical[1]), 
			width=2, tags=(self.name_tag,)
		)

		self.dots_id = []
		for i in self.control_indexes:
			delt = self.target_index - i
			if self.up:
				y_dot = y - delt * 2 * self.c
			else:
				y_dot = y + delt * 2 * self.c
			self.dots_id.append(
				self.canvas.create_oval(
					(x - 3, y_dot - 3), 
					(x + 3, y_dot + 3), 
					fill="black", tags=(self.name_tag,)
				)
			)       

	def reset_coordinates(self, **kwargs):
		if 'x_delta' in kwargs and 'y_delta' in kwargs:
			self.center_point = (
				self.center_point[0] + kwargs['x_delta'],
				self.center_point[1] + kwargs['y_delta']
			)

	def get_dots_ys(self):
		return [self.canvas.coords(dot_id)[1] + 3 for dot_id in self.dots_id]
