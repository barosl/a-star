#!/usr/bin/env python

from PySide.QtGui import *
from PySide.QtCore import *
import sys
from a_star import srch_path, State
import thread
import re

PUZZLE_SIZE = 4
CELL_W = CELL_H = 50
CELL_LINE_STEP = 10
INPUT_FPATH = 'input.txt'

class StateWnd(QWidget):
	def __init__(self, parent, p_size, cell_w=CELL_W, cell_h=CELL_H):
		super(StateWnd, self).__init__(parent)

		self.p_size = p_size
		self.cell_w = cell_w
		self.cell_h = cell_h

		self.st = None
		self.path_pts = None

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

		self.draw_path_pts(pa)

	def draw_path_pts(self, pa):
		if not self.path_pts: return

		pa.setPen(QPen(QBrush(QColor(255, 0, 0)), 3))

		prev_x, prev_y = -1, -1
		for x, y in self.path_pts:
			if prev_x != -1:
				pa.drawLine(prev_x, prev_y, x, y)

			prev_x, prev_y = x, y

	def set_st(self, st):
		self.st = st
		self.update()

	def set_path_pts(self, path_pts):
		self.path_pts = path_pts
		self.update()

class ResultWnd(QWidget):
	def __init__(self, parent, p_size):
		super(ResultWnd, self).__init__(parent)

		self.p_size = p_size

		self.sts = []
		self.st_idx = -1
		self.path_pts = []

		self.state_g = StateWnd(self, p_size)
		self.prev_st_g = QPushButton(u'&Previous State', self)
		self.next_st_g = QPushButton(u'&Next State', self)
		self.text_g = QLabel(self)

		self.prev_st_g.clicked.connect(self.on_prev_st)
		self.next_st_g.clicked.connect(self.on_next_st)

		self.update_text()

		lt_res_butts = QHBoxLayout()
		lt_res_butts.addWidget(self.prev_st_g)
		lt_res_butts.addWidget(self.next_st_g)

		lt_main = QVBoxLayout()
		lt_main.addWidget(self.state_g)
		lt_main.addLayout(lt_res_butts)
		lt_main.addWidget(self.text_g)
		lt_main.setAlignment(Qt.AlignTop)

		self.setLayout(lt_main)

		self.show()

	def set_st(self, st):
		self.sts = []
		def add_path(st):
			if st.parent: add_path(st.parent)
			self.sts.append(st)
		add_path(st)

		self.set_st_idx(0)

		self.state_g.set_path_pts(self.get_path_pts())

	def get_path_pts(self):
		path_pts = []

		x_used = {}
		y_used = {}

		prev_x, prev_y = -1, -1
		prev_pt_x, prev_pt_y = -1, -1
		for st in self.sts:
			x = st.empty_pos % self.p_size
			y = st.empty_pos / self.p_size

			pt_x = x*CELL_W + CELL_W/2
			pt_y = y*CELL_H + CELL_H/2

			if prev_x != -1:
				if prev_x == x:
					pt_x = prev_pt_x

					for delta in xrange(0, CELL_H/2, CELL_LINE_STEP):
						if pt_y - delta not in y_used: pt_y -= delta; break
						if pt_y + delta not in y_used: pt_y += delta; break
				else:
					pt_y = prev_pt_y

					for delta in xrange(0, CELL_W/2, CELL_LINE_STEP):
						if pt_x - delta not in x_used: pt_x -= delta; break
						if pt_x + delta not in x_used: pt_x += delta; break

			x_used[pt_x] = None
			y_used[pt_y] = None

			path_pts.append([pt_x, pt_y])

			prev_x, prev_y = x, y
			prev_pt_x, prev_pt_y = pt_x, pt_y

		return path_pts

	def set_st_idx(self, idx):
		if idx < 0 or idx >= len(self.sts): return

		self.state_g.set_st(self.sts[idx])
		self.st_idx = idx

		self.update_text()

	def on_prev_st(self):
		self.set_st_idx(self.st_idx-1)

	def on_next_st(self):
		self.set_st_idx(self.st_idx+1)

	def update_text(self):
		depth_s = str(len(self.sts)-1) if self.sts else '?'
		st_idx_s = '%d of %d' % (self.st_idx+1, len(self.sts)) if self.sts else '?'
		self.text_g.setText(u'Depth: %s\nState: %s' % (depth_s, st_idx_s))

class MainWnd(QWidget):
	def __init__(self):
		super(MainWnd, self).__init__()

		self.stas = []
		self.sta_idx = -1

		self.res_g = ResultWnd(self, PUZZLE_SIZE)
		self.sta_g = StateWnd(self, PUZZLE_SIZE, CELL_W/2, CELL_H/2)
		self.goal_g = StateWnd(self, PUZZLE_SIZE, CELL_W/2, CELL_H/2)
		self.srch_path_g = QPushButton(u'&Search Path', self)
		self.prev_sta_g = QPushButton(u'&Previous Start', self)
		self.next_sta_g = QPushButton(u'&Next Start', self)
		self.text_g = QLabel(self)

		self.srch_path_g.clicked.connect(self.on_srch_path)
		self.srch_path_g.setFocus()
		self.srch_path_done.connect(self.on_srch_path_done)
		self.prev_sta_g.clicked.connect(self.on_prev_sta)
		self.next_sta_g.clicked.connect(self.on_next_sta)

		self.update_text()

		lt_panel = QVBoxLayout()
		lt_panel.addWidget(self.sta_g)
		lt_panel.addWidget(self.goal_g)
		lt_panel.addWidget(self.srch_path_g)
		lt_panel.addWidget(self.next_sta_g)
		lt_panel.addWidget(self.prev_sta_g)
		lt_panel.addWidget(self.text_g)

		lt_main = QHBoxLayout()
		lt_main.addWidget(self.res_g)
		lt_main.addLayout(lt_panel)

		self.setLayout(lt_main)

		self.goal_g.set_st(State(range(1, PUZZLE_SIZE*PUZZLE_SIZE)+[0], None, None))
		self.load_stas()

		self.setWindowTitle(u'A* algorithm')
		self.show()

	def on_srch_path(self):
		def thrd():
			st = srch_path(self.sta_g.st, self.goal_g.st)
			self.srch_path_done.emit(st)

		thread.start_new_thread(thrd, ())

	srch_path_done = Signal(object)
	def on_srch_path_done(self, st):
		if not st:
			QMessageBox.critical(self, None, u'Path not found.')
			return

		self.res_g.set_st(st)

	def load_stas(self):
		stas = []

		for line in open(INPUT_FPATH).read().splitlines():
			cells = [int(x) for x in re.findall('[0-9]+', line)[:PUZZLE_SIZE*PUZZLE_SIZE]]
			assert len(cells) == PUZZLE_SIZE*PUZZLE_SIZE

			stas.append(State(cells, None, self.goal_g.st))

		self.stas = stas

		if self.stas: self.set_sta_idx(0)

	def set_sta_idx(self, sta_idx):
		if sta_idx < 0 or sta_idx >= len(self.stas): return

		self.sta_g.set_st(self.stas[sta_idx])
		self.sta_idx = sta_idx

		self.update_text()

	def on_prev_sta(self):
		self.set_sta_idx(self.sta_idx-1)

	def on_next_sta(self):
		self.set_sta_idx(self.sta_idx+1)

	def update_text(self):
		sta_idx_s = '%d of %d' % (self.sta_idx+1, len(self.stas)) if self.stas else '?'
		self.text_g.setText(u'Start node: %s' % sta_idx_s)

def main():
	app = QApplication(sys.argv)

	wnd = MainWnd()

	app.exec_()

if __name__ == '__main__':
	main()
