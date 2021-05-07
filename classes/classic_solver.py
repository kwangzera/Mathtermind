import discord
from itertools import combinations as c


class ClassicSolver:
    def __init__(self, rounds, matches):
        self.rounds = rounds
        self.matches = matches
        self.combos = list(c(range(1, 16), 3))
        self.valid = []
        self.valid_cnt = 0
        self.sol_panel = discord.Embed(title="Possible Combiations")

    def solve(self):
        for i, j, k in self.combos:
            flag = True

            for rnd, mt in zip(self.rounds, self.matches):
                if (i in rnd) + (j in rnd) + (k in rnd) != mt:
                    flag = False
                    break

            if flag:
                self.valid.append(f"`{i} {j} {k}`")
                self.valid_cnt += 1

        self.gen_embed()

    def gen_embed(self):
        if self.valid_cnt > 50:
            self.sol_panel.description = f"Solutions ({self.valid_cnt} in current gamestate) will not be listed since there are over 50 possible valid combos"
        else:
            tmpstr = ", ".join(self.valid)
            self.sol_panel.description = f"Foind {self.valid_cnt} valid solution(s):\n||{tmpstr}||"
