from tkinter import *
from .schema_editor import EditorFrame

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
		self.root.geometry('%dx%d' % (width, height))
		self.root.resizable(False, False)

		self._set_up_buttons()

	def _set_up_buttons(self):
		label = Label(self.root, text="Число линий на схеме")
		label.grid(row=1, column=0)

		opts = [str(i) for i in range(1,7)]
		self.input_lines_num = StringVar(self.root, opts[2])
		w = OptionMenu(self.root, self.input_lines_num, *opts)
		w.grid(row=1, column=1)

		self.create_window_button = Button(
			self.root, text="Add Schema Editor", fg="black",
			command=lambda: EditorFrame(
				parent_window=self, 
				parent_size=self._get_window_size(), 
				lines_num=self.input_lines_num.get()
			)
		)
		self.create_window_button.grid(row=2)

	def _get_window_size(self):
		self.root.update_idletasks()
		coords = self.root.geometry().split('+')
		return [int(coords[1]), int(coords[2])]  # width, height