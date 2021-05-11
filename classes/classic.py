from random import sample

import discord
from discord import Colour


class Classic:
    def __init__(self, discord_tag):
        self.rounds = []
        self.matches = []
        self.verified = []
        self.round_number = 0
        self.game_over = 0  # 1: win, 2: lose
        self.answer = sorted(sample(range(1, 16), 3))

        # Embeds
        self.log_msg = discord.Embed()
        self.board = discord.Embed()
        self.board_items = [f"{discord_tag}'s Classic Game"]

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
            self.log_msg = discord.Embed(
                title=self.board_items[0],
                description=":tada: Contratulations! You won!",
                colour=Colour.green()
            )
            self.game_over = 1
            return

        if self.lose():
            self.log_msg = discord.Embed(
                title=self.board_items[0],
                description=f":monkey: You lost. The answer was `{', '.join(map(str, self.answer))}`.",
                colour=Colour.red()
            )
            self.game_over = 2
            return

    def create_board(self):
        embed = discord.Embed(title=self.board_items[0])

        for elem in self.board_items[1:]:
            embed.add_field(name=elem[0], value=elem[1], inline=False)

        return embed

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

        if not (self.valid_len(guess) and self.is_unique(guess) and self.in_range(guess)):
            flag = False

        if not flag:
            self.log_msg = discord.Embed(
                description="Please input a valid guess",
                colour=Colour.red()
            )

        if self.last_guess(guess, flag):
            self.log_msg = discord.Embed(
                description="Please input 3 numbers as your final guess",
                colour=Colour.red()
            )
            flag = False

        return flag
