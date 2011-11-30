#!/usr/bin/env python

from heapq import heappush, heappop
import math
import random

PUZZLE_SIZE = 4
EMPTY_CELL = 0

class State:
	def __init__(self, cells, parent, goal):
		self.cells = cells
		self.parent = parent
		self.goal = goal
		self.size = int(math.sqrt(len(cells))); assert self.size*self.size == len(cells)
		self.empty_pos = self.cells.index(EMPTY_CELL)

		self.dist = parent.dist+1 if parent else 0
		self.heur = self.dist + self.get_cost()

	def get_cost(self):
		return len([None for x, y in zip(self.goal.cells, self.cells) if not x and not y and x != y]) if self.goal else 0

	def __repr__(self):
		return ' '.join(str(x) for x in self.cells)

	def __cmp__(self, other):
		return self.heur - other.heur

	def get_next_poses(self, empty_pos):
		poses = []
		x = empty_pos % self.size
		y = empty_pos / self.size

		if x != 0: poses.append(empty_pos - 1)
		if x != self.size-1: poses.append(empty_pos + 1)
		if y != 0: poses.append(empty_pos - self.size)
		if y != self.size-1: poses.append(empty_pos + self.size)

		return poses

	def get_nexts(self):
		for pos in self.get_next_poses(self.empty_pos):
			new_cells = self.cells[:pos] + [EMPTY_CELL] + self.cells[pos+1:]
			new_cells[self.empty_pos] = self.cells[pos]

			yield State(new_cells, self, self.goal)

	def __hash__(self):
		return hash(tuple(self.cells))

	def shuffle(self, cnt=10):
		empty_pos = self.empty_pos
		cells = self.cells

		for i in xrange(cnt):
			pos = random.choice(self.get_next_poses(empty_pos))

			new_cells = cells[:pos] + [EMPTY_CELL] + cells[pos+1:]
			new_cells[empty_pos] = cells[pos]

			empty_pos = pos
			cells = new_cells

		self.cells = new_cells
		self.empty_pos = empty_pos

def srch_path(sta, goal):
	que = []
	que_d = {}
	visited = {}

	heappush(que, sta)
	que_d[sta] = sta

	while que:
		st = heappop(que)
		del que_d[st]

		visited[st] = None

		if st.cells == goal.cells:
			return st

		for new_st in st.get_nexts():
			if new_st in visited: continue

			old_st = que_d.get(new_st, None)
			if old_st:
				if new_st.heur < old_st.heur:
					print '!!!'
			else:
				heappush(que, new_st)
				que_d[new_st] = new_st

	return None

def print_path(st):
	if st.parent: print_path(st.parent)
	print st

def main():
	goal = State(range(1, PUZZLE_SIZE*PUZZLE_SIZE)+[0], None, None)

	sta = State(goal.cells[:], None, goal)
	sta.shuffle(20)

#	goal = State([2, 4, 8, 3, 10, 5, 0, 11, 12, 14, 9, 7, 1, 13, 6, 15], None, None)
#	sta = State([0, 2, 4, 3, 10, 5, 8, 11, 12, 14, 9, 7, 1, 13, 6, 15], None, goal)

#	sta = State([5, 1, 2, 8, 9, 4, 3, 11, 10, 14, 6, 7, 13, 0, 15, 12], None, goal)
#	sta = State([1, 3, 4, 8, 5, 2, 7, 12, 9, 6, 11, 15, 13, 0, 10, 14], None, goal)
#	sta = State([1, 2, 4, 8, 5, 6, 3, 0, 9, 10, 7, 11, 13, 14, 15, 12], None, goal)

	st = srch_path(sta, goal)
	if not st:
		print >> sys.stderr, '* Path not found.'
		sys.exit(1)

	print '* %d steps needed.' % st.dist
	print_path(st)

if __name__ == '__main__':
	main()
