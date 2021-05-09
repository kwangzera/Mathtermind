import discord
from discord import Colour
from random import sample


class Classic:
    def __init__(self, discord_tag):
        self.answer = sorted(sample(range(1, 16), 3))
        self.rounds = []
        self.matches = []
        self.round_number = 0
        self.game_over = 0  # 1: win, 2: lose
        self.log_msg = discord.Embed()
        self.board = discord.Embed()
        self.board_items = [f"{discord_tag}'s Classic Game"]

    def add_round(self, guess):
        """Updates this Classic game class with a new round. Assumes `guess` is valid"""

        self.round_number += 1
        self.rounds.append(guess)
        self.matches.append(self.match_ans(guess))

        if self.matches[-1] == len(guess) == 3:
            self.log_msg = discord.Embed(
                title=self.board_items[0],
                description=":tada: Contratulations! You won!",
                colour=Colour.green()
            )
            self.game_over = 1
            return

        if self.round_number == 8:
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
        match = 0

        for num in guess:
            if num in self.answer:
                match += 1

        return match

    def valid_guess(self, guess):
        flag = True

        # Check length
        if not guess or len(guess) > 4:
            flag = False

        # Check uniqueness
        if sorted(list(set(guess))) != sorted(guess):
            flag = False

        # Check ranges
        for g in guess:
            if g < 1 or g > 15:
                flag = False

        if not flag:
            self.log_msg = discord.Embed(
                description="Please input a valid guess",
                colour=Colour.red()
            )

        if self.round_number == 7 and len(guess) != 3 and flag:
            self.log_msg = discord.Embed(
                description="Please input 3 numbers as your final guess",
                colour=Colour.red()
            )
            flag = False

        return flag
