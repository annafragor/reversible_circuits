from elements.toffoli_gate import ToffoliGate
from elements.main_frame import mainFrame
from tkinter import *


if __name__ == '__main__':
	root = Tk()
	mf = mainFrame(root, lines_num=3)
	mf.addToffoliGate(0, "Tof1", 15, 15)
	mf.addToffoliGate(2, "Tof2", 40, 40)
	mf.addToffoliGate(2, "Tof3", 70, 40)
	mf.addToffoliGate(1, "Tof4", 100, 40)
	root.mainloop()
	