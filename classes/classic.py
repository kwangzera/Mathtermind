from collections import Counter
from random import sample

import discord
from discord import Colour


class Classic:
    def __init__(self, ctx):
        # Changeable settings
        self.round_number = 0
        self.game_over = 0  # 1: lose, 2: win
        self.logging = True  # logging variable for other gamemodes are unused (placeholder)
        self.rounds = []
        self.matches = []
        self.verified = []  # Used in detective mode, all guesses here are verified
        self.board_info = []  # Contains the guess history to be displayed on the board

        # Unchangeable settings
        self.game_id = 0
        self.sets_dict = {"rl": 15, "gsl": 4, "mg": 7, "ca": None}  # Classic mode default settings (see gamemodes.py)
        self.answer = sorted(sample(range(1, 16), 3))

        # Embeds
        self.log_msg = discord.Embed(color=Colour.red())
        self.game_over_msg = discord.Embed(title=f"{ctx.author}'s Classic Game")
        self.board = discord.Embed(title=f"{ctx.author}'s Classic Game")

    def win(self, guess):
        return self.matches[-1] == len(guess) == len(self.answer)  # 3 numbers, 3 matches

    def lose(self):
        return self.round_number == self.sets_dict["mg"] + 1

    def update_stats(self, guess):
        """Executes all necessary operations after a user makes a guess"""

        self.round_number += 1
        self.rounds.append(guess)
        self.matches.append(self.match_ans(guess))
        self.verified.append(True)

    def add_round(self, guess):
        """Updates the Classic game with a new round"""

        self.update_stats(guess)

        if self.win(guess):
            self.game_over_msg.description = ":tada: Contratulations! You won!"
            self.game_over_msg.colour = Colour.green()
            self.game_over = 2
            return

        if self.lose():
            self.game_over_msg.description = f":monkey: You lost. The answer was `{', '.join(map(str, self.answer))}`."
            self.game_over_msg.colour = Colour.red()
            self.game_over = 1
            return

    def match_ans(self, guess):
        # Number of matches is sum of values from the intersection of 2 counters
        return sum((Counter(guess) & Counter(self.answer)).values())

    def valid_len(self, guess):
        # Doesn't take final guess into account
        return (guess and len(guess) <= self.sets_dict["gsl"]) or self.round_number == self.sets_dict["mg"]

    def is_unique(self, guess):
        # Set of numbers must be the same as the numbers (no duplicates)
        return sorted(set(guess)) == guess

    def in_range(self, guess):
        for g in guess:
            if g < 1 or g > self.sets_dict["rl"]:
                return False

        return True

    def last_guess(self, guess, flag):
        # `flag` makes sure the guess is valid
        return self.round_number == self.sets_dict["mg"] and len(guess) != len(self.answer) and flag

    def valid_guess(self, guess):
        """Checks if a guess is valid or not by making use of the previous helper methods."""

        flag = True

        if not self.valid_len(guess) or not self.in_range(guess):
            self.log_msg.description = f"""Please input 1 {f"to {self.sets_dict['gsl']} numbers" if self.sets_dict['gsl'] != 1 else "number only"}"""
            flag = False

        if not self.in_range(guess):
            self.log_msg.description = f"""Please input {f"numbers from 1 to {self.sets_dict['rl']}" if self.sets_dict['rl'] != 1 else "1 as your only guess"}"""
            flag = False

        if not self.is_unique(guess):
            self.log_msg.description = f"Please make sure all numbers in your guess are unique"
            flag = False

        if self.last_guess(guess, flag):
            self.log_msg.description = f"Please input {len(self.answer)} number{'s'*(len(self.answer)!=1)} as your final guess"
            flag = False

        return flag

    def gen_board(self, page, pages):
        """Initializes a gameboard to display guess history"""

        self.board.clear_fields()

        # Array slicing to get up to 10 rounds for the `page`th page
        for nm, val in self.board_info[page*10:(page+1)*10]:
            self.board.add_field(name=nm, value=val, inline=False)

        # More than 10 rounds, pagination required
        if pages > 1:
            self.board.set_footer(text=f"Page {page+1}/{pages}")
