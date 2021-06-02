import discord
from discord import Colour
from discord.ext import commands


class Gamestats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.valid_emb = discord.Embed(color=Colour.green())
        self.invalid_emb = discord.Embed(color=Colour.red())

        # Storing dict of users in bot, also reload doesn't erase gamestates
        # TODO hasattr another dict for stats

    @commands.command(aliases=["lg"])
    async def logging(self, ctx, toggle: bool = None):
        """Shows user's data logging status or toggles it on or off"""
        ...

    @commands.command()
    async def raw(self, ctx):
        """Outputs the user's raw game data as a .txt file"""
        ...

    @commands.command(aliases=["rs"])
    async def reset(self, ctx):
        """Resets the user's game data"""
        ...

    @commands.command(aliases=["st"])
    async def stats(self, ctx):
        """Displays a detailed table of the user's game stats"""
        ...

    def key(self, ctx):
        """Returns unique identification key: (user id, server id)"""

        return ctx.author.id, ctx.guild.id


def setup(bot):
    bot.add_cog(Gamestats(bot))
