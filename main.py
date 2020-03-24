from elements.toffoli_gate import ToffoliGate
from elements.main_frame import mainFrame
from tkinter import *


if __name__ == '__main__':
	root = Tk()
	mf = mainFrame(root, lines_num=3)
	root.mainloop()
	