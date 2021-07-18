from random import random, sample

from classes.classic import Classic


class Repeat(Classic):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.game_id = 1
        self.answer = self.create_answer()

        # Embeds
        self.game_over_msg.title = f"{ctx.author}'s Repeat Game"
        self.board.title = f"{ctx.author}'s Repeat Game"

    def is_unique(self, guess):
        return True  # Uniqueness doesn't matter for repeat mode

    def create_answer(self):
        """Generates the winning combination for repeat mode"""

        rng = random()*100
        a, b = sample(range(1, 16), 2)  # Not sorted

        if rng < 5:  # 5% chance of generating 3 duplicates
            return sorted((a, a, a))
        elif rng < 60:  # 55% chance of generating 2 duplicates
            return sorted((a, a, b))
