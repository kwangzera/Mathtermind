import discord
from discord import Colour
from discord.ext import commands

from classes.classic import Classic
from classes.repeat import Repeat
from classes.detective import Detective


class Gamemodes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.valid_emb = discord.Embed(title="Success", color=Colour.green())
        self.invalid_emb = discord.Embed(title="Error", color=Colour.red())

        # Storing dict of users in bot, also reload doesn't erase gamestates
        if not hasattr(bot, "games"):
            bot.games = {}

    async def cog_before_invoke(self, ctx):
        self.valid_emb.set_footer(text=ctx.author)
        self.invalid_emb.set_footer(text=ctx.author)

    @commands.command(aliases=["cl"])
    async def classic(self, ctx):
        """Starts a Mathtermind game in classic mode

        7 guesses to find the winning combo, 8th guess to determine it
        Each guess consists of 1 to 4 unique numbers
        Winning combo consists of 3 unique numbers from 1 to 15
        """

        await self.create_game(ctx, Classic(ctx))

    @commands.command(aliases=["rp"])
    async def repeat(self, ctx):
        """Starts a Mathtermind game in repeat mode

        The winning combo and user's guesses do not have to contain unique numbers
        Otherwise, the same rules follow for classic mode [;help classic]
        """

        await self.create_game(ctx, Repeat(ctx))

    @commands.command(aliases=["lie"])
    async def detective(self, ctx):
        """Starts a Mathtermind game in detective mode

        Description
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
