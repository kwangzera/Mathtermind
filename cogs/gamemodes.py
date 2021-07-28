import discord
from discord import Colour
from discord.ext import commands

from classes.classic import Classic
from classes.repeat import Repeat
from classes.detective import Detective
from classes.custom import Custom


class Gamemodes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Storing dict of users in bot
        if not hasattr(bot, "games"):
            bot.games = {}

    @commands.command(aliases=["cl"])
    @commands.cooldown(rate=1, per=1, type=commands.BucketType.member)
    async def classic(self, ctx):
        """Starts a Mathtermind game in classic mode

        A winning combination of 3 unique numbers is randomly selected and the user's
        goal is to guess those numbers. The user is given 7 guesses to try to figure out
        what the winning combination is and an 8th to determine it.

        For this gamemode, the user is allowed to guess 1 to 4 unique numbers each
        round. After each guess the game will respond with the number of numbers in the
        winning combination that match those in the user's guess.

        On the final round, the user is required to make a duplicate-free guess of the
        same size as the winning combination. If the user's guess (in any particular
        order) matches the winning combination, they win. Otherwise, they lose.

        Enter ;classic to start the game or see ;help guess for more detailed
        information about guessing.
        """

        await self.create_game(ctx, Classic(ctx))

    @commands.command(aliases=["rp"])
    @commands.cooldown(rate=1, per=1, type=commands.BucketType.member)
    async def repeat(self, ctx):
        """Starts a Mathtermind game in repeat mode

        A winning combination of 3 numbers (not necessarily unique) is randomly selected
        and the user's goal is to guess those numbers. The user is given 7 guesses to
        try to figure out what the winning combination is and an 8th to determine it.

        For this gamemode, the user is allowed to guess 1 to 4 numbers each round.
        After each guess the game will respond with the number of numbers in the winning
        combination that match those in the user's guess.

        On the final round, the user is required to make a guess of the same size as the
        winning combination. If the user's guess (in any particular order) matches the
        winning combination, they win. Otherwise, they lose.

        Enter ;repeat to start the game or see ;help guess for more detailed information
        about guessing.
        """

        await self.create_game(ctx, Repeat(ctx))

    @commands.command(aliases=["lie"])
    @commands.cooldown(rate=1, per=1, type=commands.BucketType.member)
    async def detective(self, ctx):
        """Starts a Mathtermind game in detective mode

        A winning combination of 3 unique numbers is randomly selected and the user's
        goal is to guess those numbers. The user is given 8 guesses to try to figure out
        what the winning combination is and a 9th to determine it. However, with an
        extra guess comes with a twist.

        For this gamemode, the user is allowed to guess 1 to 4 unique numbers each
        round. After each guess the game will respond with the number of numbers in the
        winning combination that match those in the user's guess.

        In one of the first 4 guesses, the game will deliberately try to trick the user
        by returning an incorrect number of matches. However, the game gives the user a
        chance to try to identify which guess had an incorrect number of matches (see
        ;help identify for more details).

        On the final round, the user is required to make a duplicate-free guess of the
        same size as the winning combination. If the user's guess (in any particular
        order) matches the winning combination, they win. Otherwise, they lose.

        Enter ;detective to start the game or see ;help guess for more detailed
        information about guessing.
        """

        await self.create_game(ctx, Detective(ctx))

    @commands.command(aliases=["cs"])
    @commands.cooldown(rate=1, per=1, type=commands.BucketType.member)
    async def custom(self, ctx, *, settings: str = None):
        """Starts a Mathtermind game in custom mode

        This gamemode allows the user to play a variation of classic mode with
        customizable settings.

        The following settings are available:
            range_limit|rl       → Upper bound to the range of guessed numbers (1 to 50)
            guess_size_limit|gsl → Maximum amount of numbers in a guess (1 to 50)
            max_guesses|mg       → Rounds before the final guess (1 to 50)
            custom_answer|ca     → Custom answer settings (1 to 50 numbers)

        Individual settings are space-separated and formatted as <setting>=<value>.
        Their order doesn't matter when passed and the user doesn't have to include all
        of them. For individual settings that are excluded, the defaults for classic
        mode will be used instead. The only exception is when the user includes a range
        limit but not a custom answer.

        The command ;custom gsl=5 mg=10 range_limit=12 creates the following game:
            1 to 5 numbers allowed per guess,
            10 guesses before the final round,
            The user can guess numbers from 1 to 12,
            A winning combination of 3 numbers from 1 to 12, as opposed the default

        Generally, custom answers are comma-separated blocks of <ranges>:<choose> where
        ranges represent possible numbers to randomly pick from, and choose (defaults to
        1 if it isn't provided) represents the number of numbers to randomly pick.
        Ranges from multiple blocks can't intersect.

        There are certain operations for ranges within a block:
            x|y → Union of 2 non-intersecting ranges
            x-y → Range of numbers from x to y inclusive
            x   → A single number

        For example, ca=1|3|5-7:2,9-11,13 will generate an winning combination of:
            2 numbers from (1, 3, 5, 6, 7),
            1 number from (9, 10, 11),
            13 by itself

        To start a custom game, enter ;cs followed by some settings
        """

        await self.create_game(ctx, Custom(ctx, settings))

    async def create_game(self, ctx, gametype):
        if self.key(ctx) not in self.bot.games:
            # Check if settings are valid for custom mode
            if gametype.game_id == 3 and not gametype.valid_settings():
                return await ctx.send(embed=gametype.log_msg)

            self.bot.games[self.key(ctx)] = gametype  # Assigns a game to a user's key
            await ctx.send(embed=discord.Embed(description="Ready to play", color=Colour.green()))
        else:
            await ctx.send(embed=discord.Embed(description="You are already in a game", color=Colour.red()))

    def key(self, ctx):
        return f"{ctx.author.id}{ctx.guild.id}"


def setup(bot):
    bot.add_cog(Gamemodes(bot))
