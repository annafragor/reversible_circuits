from visual.toffoli_gate import ToffoliGateVisual
from visual.main_frame import mainFrame
from maths.transposition import Transposition
from maths.circuit import ToffoliGate
from tkinter import Tk


if __name__ == '__main__':
	root = Tk()
	mf = mainFrame(root, width=250, height=60)
	root.mainloop()
	