from collections import Counter
from random import sample

import discord
from discord import Colour


class Classic:
    def __init__(self, ctx):
        # Changeable settings
        self.round_number = 0
        self.game_over = 0  # 1: lose, 2: win
        self.logging = True
        self.rounds = []
        self.matches = []
        self.verified = []

        # Unchangeable settings
        self.game_id = 0
        self.range_limit = 15
        self.guess_limit = 4
        self.max_guesses = 7
        self.answer_limit = 3
        self.answer = sorted(sample(range(1, 16), 3))

        # Embeds
        self.log_msg = discord.Embed(color=Colour.red())
        self.game_over_msg = discord.Embed(title=f"{ctx.author}'s Classic Game")
        self.board = discord.Embed(title=f"{ctx.author}'s Classic Game")

    def win(self, guess):
        return self.matches[-1] == len(guess) == self.answer_limit  # 3 numbers, 3 matches

    def lose(self):
        return self.round_number == self.max_guesses + 1

    def update_stats(self, guess):
        """Executes all necessary operations after a user makes a guess"""

        self.round_number += 1
        self.rounds.append(guess)
        self.matches.append(self.match_ans(guess))
        self.verified.append(True)

    def add_round(self, guess):
        """Updates the Classic game with a new round. Assumes `guess` is valid."""

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
        return guess and len(guess) <= self.guess_limit

    def is_unique(self, guess):
        # Set of numbers must be the same as the numbers (no duplicates)
        return sorted(set(guess)) == sorted(guess)

    def in_range(self, guess):
        for g in guess:
            if g < 1 or g > self.range_limit:
                return False

        return True

    def last_guess(self, guess, flag):
        # `flag` makes sure the guess is valid
        return self.round_number == self.max_guesses and len(guess) != self.answer_limit and flag

    def valid_guess(self, guess):
        """Checks if a guess is valid or not. Makes use of the previous helper methods."""

        flag = True

        if not self.valid_len(guess) or not self.in_range(guess):
            self.log_msg.description = f"Please input 1 to {self.guess_limit} numbers from 1 to {self.range_limit}"
            flag = False

        if not self.is_unique(guess):
            self.log_msg.description = f"Please make sure all numbers in your guess are unique"
            flag = False

        if self.last_guess(guess, flag):
            self.log_msg.description = f"Please input {self.answer_limit} numbers as your final guess"
            flag = False

        return flag
