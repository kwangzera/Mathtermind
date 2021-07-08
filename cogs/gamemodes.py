import discord
from discord import Colour
from discord.ext import commands

from classes.classic import Classic
from classes.repeat import Repeat
from classes.detective import Detective


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

        For this gamemode, the user is allowed to guess 1 to 4 unique numbers each turn.
        After each guess the game will respond with the number of numbers in the winning
        combination that match those in the user's guess.

        On the final guess, the user is required to guess 3 unique numbers. If all 3 of
        the user's numbers (in any particular order) match the winning combination, then
        the user wins. Otherwise, the user loses.

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

        For this gamemode, the user is allowed to guess 1 to 4 numbers (remember, they
        don't have to be unique) each turn. After each guess the game will respond with
        the number of numbers in the winning combination that match those in the user's
        guess.

        On the final guess, the user is required to guess 3 unique numbers. If all 3 of
        the user's numbers (in any particular order) match the winning combination, then
        the use wins. Otherwise, the user loses.

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

        For this gamemode, the user is allowed to guess 1 to 4 unique numbers each turn.
        After each guess the game will tell the user the number of numbers in the
        winning combination that match those in the user's guess.

        In one of the first 4 guesses, the game will deliberately try to trick the user
        by returning an incorrect number of matches. However, the game gives the user a
        chance to try to identify which guess had an incorrect number of matches (see
        ;help identify for more details)

        On the final guess, the user is required to guess 3 unique numbers. If all 3 of
        the user's numbers (in any particular order) match the winning combination, then
        the user wins. Otherwise, the user loses.

        Enter ;detective to start the game or see ;help guess for more detailed
        information about guessing.
        """

        await self.create_game(ctx, Detective(ctx))

    async def create_game(self, ctx, gametype):
        if self.key(ctx) not in self.bot.games:
            self.bot.games[self.key(ctx)] = gametype  # Assigns a game to a user's key
            await ctx.send(embed=discord.Embed(description="Ready to play", color=Colour.green()))
        else:
            await ctx.send(embed=discord.Embed(description="You are already in a game", color=Colour.red()))

    def key(self, ctx):
        return f"{ctx.author.id}{ctx.guild.id}"


def setup(bot):
    bot.add_cog(Gamemodes(bot))
