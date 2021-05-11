from random import randint, choice

from classes.classic import Classic


class Detective(Classic):
    def __init__(self, discord_tag):
        super().__init__(discord_tag)
        self.board_items = [f"{discord_tag}'s Detective Game"]
        self.lie_guess = randint(1, 4)  # Index of the lie
        self.actual = 0  # Real number of matches
        print(self.lie_guess)

    def match_ans(self, guess):
        tmp_guess = list(guess)
        match = 0

        for num in self.answer:
            if num in tmp_guess:
                tmp_guess.remove(num)
                match += 1

        if self.round_number == self.lie_guess:
            self.actual = match
            return self.create_lie(match, len(guess))
        else:
            return match

    def lose(self):
        return self.round_number == 9

    def last_guess(self, guess, flag):
        return self.round_number == 8 and len(guess) != 3 and flag

    def create_lie(self, actual, guess_len):
        """Returns a random number from 0 to `guess_len` that is not `actual`"""

        st = set(range(guess_len+1)) - {actual}
        return choice(list(st))
