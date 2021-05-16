from random import choice, sample, choices

import discord

from classes.classic import Classic


class Repeat(Classic):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.game_id = 1
        self.answer = self.create_answer()
        self.game_over_msg.title = f"{ctx.author}'s Repeat Game"
        self.board.title = f"{ctx.author}'s Repeat Game"
        print(self.answer)

    # Uniqueness doesn't matter for repeat mode
    def is_unique(self, guess):
        return True

    def create_answer(self):
        rng = choice([0, 1, 1, 1, 2])
        a, b = sample(range(1, 16), 2)

        if rng == 1:
            return sorted((a, a, b))
        elif rng == 2:
            return sorted((a, a, a))
