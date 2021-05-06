from pprint import pprint
from itertools import combinations as c


class ClassicSolver:
    def __init__(self, rounds, matches):
        self.rounds = rounds
        self.matches = matches
        self.combos = list(c(range(1, 16), 3))
        self.valid = []

    def solve(self):
        for i, j, k in self.combos:
            flag = True

            for rnd, mt in zip(self.rounds, self.matches):
                if (i in rnd) + (j in rnd) + (k in rnd) != mt:
                    flag = False
                    break

            if flag:
                self.valid.append((i, j, k))

            # print()

# cs = ClassicSolver([(1, 2, 3, 4), (2, 7, 8), (9, 10, 11, 12), (13, 14, 15), (3,7,8), (4,8), (1,)], [2,1,0,0,2,0,1])
#
# cs.solve()
# pprint(cs.valid)
