from collections import Counter as Cnt
from itertools import combinations as c

import discord


class ClassicSolver:
    def __init__(self, rounds, matches, verified):
        self.rounds = rounds
        self.matches = matches
        self.verified = verified
        self.valid = []
        self.valid_cnt = 0
        self.combos = list(c(range(1, 16), 3))
        self.sol_panel = discord.Embed()

    def solve(self):
        for cb in self.combos:
            for rnd, mt, vr in zip(self.rounds, self.matches, self.verified):
                if not vr:
                    continue

                # TODO explain this
                cnt = sum((Cnt(cb) & Cnt(rnd)).values())

                if cnt != mt:
                    break
            else:
                self.valid.append(f"`{cb[0]} {cb[1]} {cb[2]}`")
                self.valid_cnt += 1

        self.gen_embed()

    def gen_embed(self):
        self.sol_panel.title = f"{self.valid_cnt} Valid Solution{'s'*(self.valid_cnt != 1)} Found"

        if self.valid_cnt > 64:
            self.sol_panel.description = f"Solutions will not be listed since there are over 64 possible valid combinations"
        else:
            self.sol_panel.description = f"||{', '.join(self.valid)}||"
