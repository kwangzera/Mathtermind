from random import choices

from classes.classic import Classic


class Repeat(Classic):
    def __init__(self, discord_tag):
        super().__init__(discord_tag)
        self.board_items = [f"{discord_tag}'s Repeat Game"]
        self.answer = sorted(choices(range(1, 16), k=3))
        print(self.answer)

    # Uniqueness doesn't matter for repeat mode
    def is_unique(self, guess):
        return True
