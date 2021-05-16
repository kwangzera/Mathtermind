import discord
from discord import Colour
from discord.ext import commands

from classes.classic import Classic
from classes.repeat import Repeat
from classes.detective import Detective


class Gamemodes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.valid_emb = discord.Embed(color=Colour.green())
        self.invalid_emb = discord.Embed(color=Colour.red())

        # Storing dict of users in bot, also reload doesn't erase gamestates
        if not hasattr(bot, "games"):
            bot.games = {}

    @commands.command(aliases=["cl"])
    async def classic(self, ctx):
        """Starts a Mathtermind game in classic mode"""

        await self.create_game(ctx, Classic(ctx))

    @commands.command(aliases=["rp"])
    async def repeat(self, ctx):
        """Starts a Mathtermind game in repeat mode"""

        await self.create_game(ctx, Repeat(ctx))

    @commands.command(aliases=["lie"])
    async def detective(self, ctx):
        """Starts a Mathtermind game in detective mode


        """
        await self.create_game(ctx, Detective(ctx))

    async def create_game(self, ctx, gametype):
        if self.key(ctx) not in self.bot.games:
            self.bot.games[self.key(ctx)] = gametype
            self.valid_emb.description = "Ready to play"
            await ctx.send(embed=self.valid_emb)
        else:
            self.invalid_emb.description = "User is already in a game"
            await ctx.send(embed=self.invalid_emb)

    def key(self, ctx):
        """Each game is unique based on the player and the guild"""

        return ctx.author.id, ctx.guild.id


def setup(bot):
    bot.add_cog(Gamemodes(bot))
