from random import sample

import discord
from discord import Colour


class Classic:
    def __init__(self, ctx):
        self.game_id = 0
        self.rounds = []
        self.matches = []
        self.verified = []
        self.round_number = 0
        self.game_over = 0  # 1: win, 2: lose
        self.answer = sorted(sample(range(1, 16), 3))

        # Embeds
        self.log_msg = discord.Embed(title="Error", color=Colour.red())
        self.log_msg.set_footer(text=ctx.author)

        self.game_over_msg = discord.Embed(title="Game Ended")
        self.game_over_msg.set_footer(text=ctx.author)

        self.board = discord.Embed(title="Classic Gamemode")
        self.board.set_footer(text=ctx.author)

        self.board_items = "placeholder"

    def win(self, guess):
        return self.matches[-1] == len(guess) == 3

    def lose(self):
        return self.round_number == 8

    def update_stats(self, guess):
        self.round_number += 1
        self.rounds.append(guess)
        self.matches.append(self.match_ans(guess))
        self.verified.append(True)

    def add_round(self, guess):
        """Updates this Classic game class with a new round. Assumes `guess` is valid"""

        self.update_stats(guess)

        if self.win(guess):
            self.game_over_msg.description = ":tada: Contratulations! You won!"
            self.game_over_msg.colour = Colour.green()
            self.game_over = 1
            return

        if self.lose():
            self.game_over_msg.description = f":monkey: You lost. The answer was `{', '.join(map(str, self.answer))}`."
            self.game_over_msg.colour = Colour.red()
            self.game_over = 2
            return

    def match_ans(self, guess):
        tmp_guess = list(guess)
        match = 0

        for num in self.answer:
            if num in tmp_guess:
                tmp_guess.remove(num)
                match += 1

        return match

    def valid_len(self, guess):
        return guess and len(guess) <= 4

    def is_unique(self, guess):
        return sorted(set(guess)) == sorted(guess)

    def in_range(self, guess):
        for g in guess:
            if g < 1 or g > 15:
                return False

        return True

    def last_guess(self, guess, flag):
        return self.round_number == 7 and len(guess) != 3 and flag

    def valid_guess(self, guess):
        flag = True

        if not self.valid_len(guess) or not self.in_range(guess):
            self.log_msg.description = "Please input 1 to 4 numbers from 1 to 15"
            flag = False

        if not self.is_unique(guess):
            self.log_msg.description = "Please make sure all numbers in the guess are unique"
            flag = False

        if self.last_guess(guess, flag):
            self.log_msg.description = "Please input 3 numbers as your final guess"
            flag = False

        return flag
