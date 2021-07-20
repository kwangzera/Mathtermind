from classes.classic import Classic
from random import sample


class Custom(Classic):
    def __init__(self, ctx, settings):
        super().__init__(ctx)

        # Unchangeable settings
        self.game_id = 3

        # Embeds
        self.game_over_msg.title = f"{ctx.author}'s Custom Game"
        self.board.title = f"{ctx.author}'s Custom Game"

        # Applying settings to custom game
        self.parse_settings(settings)

    def parse_settings(self, settings):
        # use this so invalid settings = break
        tmp = [self.range_lim, self.guess_sz_lim, self.max_guesses, self.answer_sz_lim, self.answer]

        for indiv in settings.split():
            try:
                set, val = indiv.split("=")
                print(set, val)

                if set in {"rl", "range_limit"}:
                    tmp[0] = int(val)
                elif set in {"gsl", "guess_size_limit"}:
                    tmp[1] = int(val)
                elif set in {"mg", "max_guesses"}:
                    tmp[2] = int(val)
                elif set in {"asl", "answer_size_limit"}:
                    tmp[3] = int(val)
                elif set in {"ca", "custom_answer"}:
                    tmp[4] = list(map(int, val.split(",")))
            except ValueError:
                print("invalid settings")
                return False

        self.range_lim = tmp[0]
        self.guess_sz_lim = tmp[1]
        self.max_guesses = tmp[2]
        self.answer_sz_lim = tmp[3]
        self.answer = tmp[4]

        return True

    def check_settings():
        ...