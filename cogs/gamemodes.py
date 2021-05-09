import discord
from discord import Colour
from discord.ext import commands

from classes.classic import Classic


class Gamemodes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Frequently used embeds
        self.ready_play = discord.Embed(
            description="Ready to play",
            color=Colour.green()
        )
        self.in_game = discord.Embed(
            description="User is already in a game",
            color=Colour.red()
        )

        # Multiple users stored in bot, reload doesn't erase gamestate
        if not hasattr(bot, "games"):
            bot.games = {}

    @commands.command(aliases=["cl"])
    async def classic(self, ctx):
        """Starts a Mathtermind game in classic mode

        7 Guesses to find winning combo, 8th Guess to determine it
        Each guess consists of 1-4 unique nubmers
        Winning combo consists of 3 unique numbers from 1-15
        """

        # TODO make this a function when more gamemodes added
        key = (ctx.author.id, ctx.guild.id)

        # TODO make this a function maybe
        if key not in self.bot.games:
            self.bot.games[key] = Classic(ctx.author)
            print(self.bot.games[key].answer)
            await ctx.send(embed=self.ready_play)
        else:
            await ctx.send(embed=self.in_game)


def setup(bot):
    bot.add_cog(Gamemodes(bot))
