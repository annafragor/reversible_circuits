from tkinter import *
from .schema_editor import *

c = 10  # constant for gate size

def _check_number(inp_str, acttyp):
			if acttyp == '1': #insert
				if not inp_str.isdigit():
					return False
			return True


class mainFrame(Frame):
	def __init__(self, root, width=600, height=300):
		Frame.__init__(self, root)
		self.root = root
		self.root.title("Главное окно")
		# self.root.geometry('%dx%d' % (300, 200))
		self.root.resizable(False, False)

		self._set_up_buttons()

	def _set_up_buttons(self):
		label = Label(self.root, text="Число линий на схеме")
		label.grid(row=1, column=0)

		self.input_lines_num = Entry(
			self.root, validate="key"
		)
		self.input_lines_num['validatecommand'] = (self.input_lines_num.register(_check_number),'%P','%d')
		self.input_lines_num.grid(row=1, column=1)

		self.create_window_button = Button(
			self.root, text="Add Schema Editor", fg="black",
			command=lambda: EditorFrame(
				parent_window=self, 
				parent_size=self._get_window_size(), 
				lines_num=self.input_lines_num.get()
			)
		)
		self.create_window_button.grid(row=2)
	
	def _create_schema_editor_window(self):
		pass

	def _get_window_size(self):
		self.root.update_idletasks()
		coords = self.root.geometry().split('+')
		return [int(coords[1]), int(coords[2])]  # width, height