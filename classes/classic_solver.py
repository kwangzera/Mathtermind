import discord
from itertools import combinations as c


class ClassicSolver:
    def __init__(self, rounds, matches):
        self.rounds = rounds
        self.matches = matches
        self.combos = list(c(range(1, 16), 3))
        self.valid = []
        self.valid_cnt = 0
        self.sol_panel = discord.Embed()

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
        self.sol_panel.title = f"{self.valid_cnt} Valid Solutions"

        if self.valid_cnt > 64:
            self.sol_panel.description = f"Solutions will not be listed since there are over 64 possible valid combos"
        else:
            self.sol_panel.description = f"||{', '.join(self.valid)}||"
