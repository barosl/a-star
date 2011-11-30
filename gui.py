#!/usr/bin/env python

from PySide.QtGui import *
from PySide.QtCore import *
import sys
from a_star import srch_path, State
import thread

PUZZLE_SIZE = 4
CELL_W = CELL_H = 50

class StateWnd(QWidget):
	def __init__(self, parent, p_size, cell_w=CELL_W, cell_h=CELL_H):
		super(StateWnd, self).__init__(parent)

		self.p_size = p_size
		self.cell_w = cell_w
		self.cell_h = cell_h

		self.st = None

		self.setMinimumSize(self.cell_w*self.p_size, self.cell_h*self.p_size)
		self.show()

	def paintEvent(self, ev):
		pa = QPainter(self)

		for i in xrange(self.p_size):
			pa.drawLine(0, i*self.cell_h, self.p_size*self.cell_w, i*self.cell_h)
			pa.drawLine(i*self.cell_w, 0, i*self.cell_w, self.p_size*self.cell_h)

		pa.drawLine(0, self.p_size*self.cell_h - 1, self.p_size*self.cell_w - 1, self.p_size*self.cell_h - 1)
		pa.drawLine(self.p_size*self.cell_w - 1, 0, self.p_size*self.cell_w - 1, self.p_size*self.cell_h - 1)

		if not self.st: return

		pa.setFont(QFont(None, min(self.cell_w/3, self.cell_h/3)))

		for i, cell in enumerate(self.st.cells):
			x = i % self.p_size
			y = i / self.p_size

			pa.drawText(x*self.cell_w, y*self.cell_h, self.cell_w, self.cell_h, Qt.AlignCenter, unicode(cell))

	def set_st(self, st):
		self.st = st
		self.update()

class ResultWnd(QWidget):
	def __init__(self, parent, p_size):
		super(ResultWnd, self).__init__(parent)

		self.p_size = p_size

		self.sts = []
		self.st_idx = -1
		self.p_lines = []

		self.state_g = StateWnd(self, p_size)
		self.state_g.move(0, 0)

		self.setMinimumSize(CELL_W*self.p_size, CELL_H*self.p_size)
		self.show()

	def set_st(self, st):
		self.sts = []
		def add_path(st):
			if st.parent: add_path(st.parent)
			self.sts.append(st)
		add_path(st)

		self.set_st_idx(0)

	def set_st_idx(self, idx):
		if idx < 0 or idx >= len(self.sts): return

		self.state_g.set_st(self.sts[idx])
		self.st_idx = idx

class MainWnd(QWidget):
	def __init__(self):
		super(MainWnd, self).__init__()

		self.res_g = ResultWnd(self, PUZZLE_SIZE)
		self.prev_g = QPushButton(u'&Previous', self)
		self.next_g = QPushButton(u'&Next', self)
		self.sta_g = StateWnd(self, PUZZLE_SIZE, CELL_W/2, CELL_H/2)
		self.goal_g = StateWnd(self, PUZZLE_SIZE, CELL_W/2, CELL_H/2)
		self.srch_g = QPushButton(u'&Search', self)

		self.goal_g.set_st(State(range(1, PUZZLE_SIZE*PUZZLE_SIZE)+[0], None, None))
		self.sta_g.set_st(State([1, 3, 4, 8, 5, 2, 7, 12, 9, 6, 11, 15, 13, 0, 10, 14], None, self.goal_g.st))

		self.srch_g.clicked.connect(self.on_srch)
		self.srch_g.setFocus()
		self.prev_g.clicked.connect(self.on_prev)
		self.next_g.clicked.connect(self.on_next)
		self.srch_done.connect(self.on_srch_done)

		lt_res_butts = QHBoxLayout()
		lt_res_butts.addWidget(self.prev_g)
		lt_res_butts.addWidget(self.next_g)

		lt_res = QVBoxLayout()
		lt_res.addWidget(self.res_g)
		lt_res.addLayout(lt_res_butts)

		lt_panel = QVBoxLayout()
		lt_panel.addWidget(self.sta_g)
		lt_panel.addWidget(self.goal_g)
		lt_panel.addWidget(self.srch_g)

		lt_main = QHBoxLayout()
		lt_main.addLayout(lt_res)
		lt_main.addLayout(lt_panel)

		self.setLayout(lt_main)

		self.show()

	def on_srch(self):
		def thrd():
			st = srch_path(self.sta_g.st, self.goal_g.st)
			self.srch_done.emit(st)

		thread.start_new_thread(thrd, ())

	srch_done = Signal(object)
	def on_srch_done(self, st):
		if not st:
			QMessageBox.critical(self, None, u'Path not found.')
			return

		self.res_g.set_st(st)

	def on_prev(self):
		self.res_g.set_st_idx(self.res_g.st_idx-1)

	def on_next(self):
		self.res_g.set_st_idx(self.res_g.st_idx+1)

def main():
	app = QApplication(sys.argv)

	wnd = MainWnd()

	app.exec_()

if __name__ == '__main__':
	main()
