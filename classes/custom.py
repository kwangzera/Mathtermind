from classes.classic import Classic
from random import sample


class Custom(Classic):
    def __init__(self, ctx, settings):
        super().__init__(ctx)

        # Changeable variables
        self.ranges = []
        self.tmp_sets = {
            "rl": None,
            "gsl": None,
            "mg": None,
            "ca": None
        }

        # Unchangeable variables
        self.game_id = 3
        self.settings = settings

        # Embeds
        self.game_over_msg.title = f"{ctx.author}'s Custom Game"
        self.board.title = f"{ctx.author}'s Custom Game"

    def create_answer(self, settings):
        answer = []

        # Splitting by times repeated
        for part in settings.split(","):
            rest, _, repeat = part.partition(":")
            range_rng = []

            if not repeat:
                repeat = "1"

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

    def is_classic(self):
        return self.settings is None

    def valid_input(self):
    def parse_settings():
        try:
            for indiv in self.settings.split():
                set, val = indiv.split("=")
                print(set, val)

                if set in {"rl", "range_limit"}:
                    tmp_sets["rl"] = int(val)
                elif set in {"gsl", "guess_size_limit"}:
                    tmp_sets["gsl"] = int(val)
                elif set in {"mg", "max_guesses"}:
                    tmp_sets["mg"] = int(val)
                elif set in {"ca", "custom_answer"}:
                    tmp_sets["ca"] = val
        except ValueError:
            return False
        else:
            return True

    def valid_settings(self):
        """
        |rl  |gsl |mg  |
        |x   |    |    |
        |    |x   |    |
        |    |    |x   |
        |x   |x   |    |
        |x   |    |x   |
        |    |x   |x   |
        |x   |x   |x   |
        """

        tmp_sets = {
            "rl": None,
            "gsl": None,
            "mg": None,
            "ca": None
        }

        # No settings passed = classic mode
        if self.is_classic():
            return True

        # Parsing settings, making sure input is valid
        if not self.valid_input():
            return False

        # Overriding missing settings with default values (temporary)
        for key, val in tmp_sets.items():
            print(key, val)
            if val is None:
                tmp_sets[key] = self.sets_dict[key]

        # Exceeding limits for custom settings
        if not (1 <= tmp_sets["rl"] <= 100) or not (1 <= tmp_sets["gsl"] <= 25) or not (1 <= tmp_sets["mg"] <= 100):
            return False

        # Isn't possible to guess more than the range of numbers without repeats
        if tmp_sets["gsl"] > tmp_sets["rl"]:
            return False

        # No custom answer provided
        if tmp_sets["ca"] is None:
            self.answer = self.create_answer(f"1-{tmp_sets['rl']}:3")
            tmp_sets["ca"] = f"1-{tmp_sets['rl']}:3"
        else:
            # TODO regex checking or smth
            self.answer = self.create_answer(tmp_sets["ca"])
            # check ans acc fits in the range

        self.ranges.sort()

        # Checks for range intersections
        # TODO add "more numbers in range" here checking
        if len(self.ranges) > 1:
            for i in range(len(self.ranges)-1):
                # Intersection exist
                if self.ranges[i][1] > self.ranges[i+1][0]:
                    return False

        # TODO max checking
        # TODO also check answer size

        # Applying custom settings
        for key, val in tmp_sets.items():
            self.sets_dict[key] = tmp_sets[key]

        return True
