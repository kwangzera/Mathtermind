from random import random, sample

from classes.classic import Classic


class Repeat(Classic):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.game_id = 1
        self.game_over_msg.title = f"{ctx.author}'s Repeat Game"
        self.board.title = f"{ctx.author}'s Repeat Game"
        self.create_answer()
        print("REPEAT", self.answer)

    # Uniqueness doesn't matter for repeat mode
    def is_unique(self, guess):
        return True

    def create_answer(self):
        rng = random()*100
        a, b = sample(range(1, 16), 2)

        if rng < 5:
            self.answer = sorted((a, a, a))
        elif rng < 60:
            self.answer = sorted((a, a, b))
