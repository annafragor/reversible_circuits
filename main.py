from visual_elements.toffoli_gate import ToffoliGateVisual
from visual_elements.main_frame import mainFrame
from maths.transposition import Transposition
from maths.circuit import ToffoliGate
from tkinter import *


if __name__ == '__main__':
	# root = Tk()
	# mf = mainFrame(root, lines_num=3)
	# root.mainloop()

	# outputs = [str(bin(elem))[2:].zfill(3) for elem in [7, 1, 4, 3, 0, 2, 6, 5]]
	# tr = Transposition(3, outputs=outputs)
	# tr.print_truth_table()
	# print()

	gates = [
		ToffoliGate(n=3, target_line_index=2, control_lines_indexes=[0, 1]),
		ToffoliGate(n=3, target_line_index=1, control_lines_indexes=[0, 2]),
		ToffoliGate(n=3, target_line_index=2, control_lines_indexes=[0, 1]),
		ToffoliGate(n=3, target_line_index=2)
	]
	tr2 = Transposition(3, gates=gates)
	tr2.print_truth_table()
	