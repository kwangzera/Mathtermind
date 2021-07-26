from collections import Counter
from random import randint, choice

from classes.classic import Classic


class Detective(Classic):
    def __init__(self, ctx):
        super().__init__(ctx)

        # Changeable variables
        self.actual_match = -1  # Real number of matches
        self.used_identify = False

        # Uncheageable variables
        self.game_id = 2
        self.lie_index = randint(1, 4)  # Index of the lie

        # Embeds
        self.game_over_msg.title = f"{ctx.author}'s Detective Game"
        self.board.title = f"{ctx.author}'s Detective Game"

    def match_ans(self, guess):
        match = sum((Counter(guess) & Counter(self.answer)).values())

        # Gives a false match if the round number is the lie index
        if self.round_number == self.lie_index:
            self.actual_match = match
            return self.create_lie(match, len(guess))
        else:
            return match

    def win(self, guess):
        # Must be a verified guess to win
        return (self.matches[-1] == len(guess) == 3) and self.round_number > 4

    def lose(self):
        return self.round_number == 9

    def update_stats(self, guess):
        self.round_number += 1
        self.rounds.append(guess)
        self.matches.append(self.match_ans(guess))

        # Rounds are guaranteed to be verified after the 4th guess
        if self.round_number <= 4:
            self.verified.append(False)
        else:
            self.verified.append(True)

    def last_guess(self, guess, flag):
        return self.round_number == 8 and len(guess) != 3 and flag

    def create_lie(self, actual, guess_len):
        """Returns a random number from 0 to `guess_len` that is not `actual`"""

        # Probabilities for all possible fake matches
        probs = {0: 6, 1: 9, 2: 4, 3: 1}
        guess_len = 3 if guess_len == 4 else guess_len

        # Filtering out the True match
        ret_probs = Counter({i: probs[i] for i in range(0, guess_len+1)})
        del ret_probs[actual]

        # Returns fake match from list of numbers with different frequencies determined by `probs`
        return choice(list(ret_probs.elements()))
