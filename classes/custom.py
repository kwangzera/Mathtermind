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
        short = ["rl", "gsl", "asl", "ca", "mg"]
        long = ["range_limit", "guess_size_limit", "answer_size_limit", "custom_answer", "max_guesses"]

        for indiv in settings.split():
            set, val = indiv.split("=")
            print(set, val)

        self.range_limit = 100
        self.guess_limit = 25
        self.max_guesses = 100
        self.answer_limit = 20
        self.answer = sorted(sample(range(1, 100+1), 10))