from classes.classic import Classic
from random import sample


class Custom(Classic):
    def __init__(self, ctx, settings):
        super().__init__(ctx)

        # Changeable variables
        self.ranges = []  # TODO turn this local

        # Unchangeable variables
        self.game_id = 3
        self.settings = settings

        # Embeds
        self.game_over_msg.title = f"{ctx.author}'s Custom Game"
        self.board.title = f"{ctx.author}'s Custom Game"

    def create_answer(self):
        answer = []

        # Splitting by times repeated
        for part in self.settings.split(","):
            rest, _, repeat = part.partition(":")
            range_rng = []

            if not repeat:
                repeat = "1"

            repeat = int(repeat)

            # Splitting by ranges
            for part in rest.split("|"):
                start, _, end = part.partition("-")

                if not end:
                    end = start

                start, end = sorted((int(start), int(end)))

                # Adding numbers to temp array for a random sample
                range_rng += range(start, end+1)
                self.ranges.append((start, end))

            answer += sample(range_rng, repeat)

        return answer

    def valid_settings(self):
        range_lim = guess_sz_lim = max_guesses = answer = None

        if self.settings is None:
            return True

        # Parsing settings / invalid settings = break
        for indiv in self.settings.split():
            try:
                set, val = indiv.split("=")
                print(set, val)

                if set in {"rl", "range_limit"}:
                    range_lim = int(val)
                elif set in {"gsl", "guess_size_limit"}:
                    guess_sz_lim = int(val)
                elif set in {"mg", "max_guesses"}:
                    max_guesses = int(val)
                elif set in {"ca", "custom_answer"}:
                    answer = val
            except ValueError:
                return False

        '''regex checking'''
        answer = self.create_answer()


        # Exceeding limits for custom settings
        if range_lim > 100 or guess_sz_lim > 25 or max_guesses > 20:
            return False

        # Checks for range intersections
        if len(self.ranges) > 1:
            for i in range(len(self.ranges)-1):
                # Intersection exist
                if self.ranges[i][1] > self.ranges[i+1][0]:
                    return False

        if range_lim < len(answer):
            return False

        self.range_lim = range_lim
        self.guess_sz_lim = guess_sz_lim
        self.max_guesses = max_guesses
        self.answer = answer

        return True
