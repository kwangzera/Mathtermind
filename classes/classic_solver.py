from collections import Counter
from itertools import combinations as c

import discord


class ClassicSolver:
    def __init__(self, rounds, matches, verified):
        self.valid_cnt = 0
        self.valid = []
        self.rounds = rounds
        self.matches = matches
        self.verified = verified  # All True for classic
        self.combos = list(c(range(1, 16), 3))

        # Embeds
        self.sol_panel = discord.Embed()

    def solve(self):
        """Brute forces all possible combinations and identifies possible ones"""

        for cb in self.combos:
            for rnd, mt, vr in zip(self.rounds, self.matches, self.verified):
                # Doesn't attempt to count matches if guess is unverified (lie mode)
                if not vr:
                    continue

                # Number of matches is sum of values from intersection of the 2 counters
                cnt = sum((Counter(cb) & Counter(rnd)).values())

                # Not a possible solution
                if cnt != mt:
                    break
            else:
                self.valid.append(f"`{cb[0]} {cb[1]} {cb[2]}`")
                self.valid_cnt += 1

        self.gen_embed()

    def gen_embed(self):
        """Creates an embed displaying all possible solutions if there are 64 or less"""

        self.sol_panel.title = f"{self.valid_cnt} Valid Solution{'s'*(self.valid_cnt != 1)} Found"

        if self.valid_cnt > 64:
            self.sol_panel.description = f"Solutions will not be listed since there are over 64 possible valid combinations"
        else:
            self.sol_panel.description = f"||{', '.join(self.valid)}||"  # Spoilers the solutions
