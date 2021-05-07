from discord.ext import commands

from classes.classic import Classic


class Gamemodes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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

        if ctx.author not in self.bot.games:
            self.bot.games[ctx.author] = Classic(ctx.author)
            await ctx.send("Ready to play")
        else:
            await ctx.send("User is already in a game")


def setup(bot):
    bot.add_cog(Gamemodes(bot))
