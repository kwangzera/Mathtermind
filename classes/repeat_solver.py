from itertools import combinations_with_replacement as cwr

from classes.classic_solver import ClassicSolver


class RepeatSolver(ClassicSolver):
    def __init__(self, rounds, matches):
        super().__init__(rounds, matches)
        self.combos = list(cwr(range(1, 16), 3))
