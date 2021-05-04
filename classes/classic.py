from random import sample


class Classic:
    rounds = []
    matches = []
    answer = []
    round_number = 0
    game_over = 0  # 1 - win, 2 - lose

    def __init__(self):
        self.answer = sample(range(1, 16), 3)

    def add_round(self, guess):
        """Updates this Classic game class with a new round. Assumes `guess` is valid"""

        self.round_number += 1
        self.rounds.append(guess)
        self.matches.append(self.match_ans(guess))

        if self.matches[-1] == len(guess) == 3:
            self.game_over = 1
            return

        if self.round_number == 8:
            self.game_over = 2
            return

    def match_ans(self, guess):
        match = 0

        for num in guess:
            if num in self.answer:
                match += 1

        return match

    # TODO custom error for last guess?
    def valid_guess(self, guess):
        # Check length
        if len(guess) > 4:
            return False
        print(self.round_number, len(guess))
        if self.round_number == 7 and len(guess) != 3:
            return False

        # Check uniqueness
        if sorted(list(set(guess))) != sorted(guess):
            return False

        # Check ranges
        for g in guess:
            if g < 1 or g > 15:
                return False

        return True
