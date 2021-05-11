from random import choice, sample, choices

from classes.classic import Classic


class Repeat(Classic):
    def __init__(self, discord_tag):
        super().__init__(discord_tag)
        self.game_id = 1
        self.board_items = [f"{discord_tag}'s Repeat Game"]
        self.answer = self.create_answer()
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
