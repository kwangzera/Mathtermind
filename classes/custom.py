from classes.classic import Classic
from random import sample


class Custom(Classic):
    def __init__(self, ctx, settings):
        super().__init__(ctx)

        # Changeable variables
        self.ranges = []
        self.tmp_settings = {
            "rl": self.range_lim,
            "gsl": self.guess_sz_lim,
            "mg": self.max_guesses,
            "ca": self.answer
        }

        # Unchangeable variables
        self.game_id = 3

        # Embeds
        self.game_over_msg.title = f"{ctx.author}'s Custom Game"
        self.board.title = f"{ctx.author}'s Custom Game"

        # Applying settings to custom game
        self.parse_settings(settings)

    def parse_settings(self, settings):
        # invalid settings = break
        for indiv in settings.split():
            try:
                set, val = indiv.split("=")
                print(set, val)

                if set in {"rl", "range_limit"}:
                    self.tmp_settings["rl"] = int(val)
                elif set in {"gsl", "guess_size_limit"}:
                    self.tmp_settings["gsl"] = int(val)
                elif set in {"mg", "max_guesses"}:
                    self.tmp_settings["mg"] = int(val)
                elif set in {"ca", "custom_answer"}:
                    self.tmp_settings["ca"] = val
            except ValueError:
                print("invalid settings")
                return False

        return True

    def create_answer(setting):
        answer = []

        # Splitting by times repeated
        for part in setting.split(","):
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

                start, end = sorted(int(start), int(end))

                # Adding numbers to temp array for a random sample
                range_rng += range(start, end+1)
                self.ranges.append((start, end))

            answer += sample(range_rng, repeat)

        self.tmp_settings["ca"] = answer

    def valid_settings():
        # Exceeding limits for custom settings
        if self.tmp_settings["rl"] > 100 or self.tmp_settings["gsl"] > 25 or self.tmp_settings["mg"] > 20:
            return False

        # Checks for range intersections
        if len(self.ranges) > 1:
            for i in range(len(self.ranges)-1):
                # Intersection exist
                if self.ranges[i][1] > self.ranges[i+1][0]:
                    return False

        if range_lim < len(self.tmp_settings["ca"]):
            return False

        self.range_lim = self.tmp_settings["rl"]
        self.guess_sz_lim = self.tmp_settings["gsl"]
        self.max_guesses = max_guesses
        self.answer = self.tmp_settings["ca"]

        return True
