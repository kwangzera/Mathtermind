from pprint import pformat

from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, extension):
        self.bot.load_extension(f"cogs.{extension}")
        await ctx.send(f"Extension {extension} loaded")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, extension):
        self.bot.unload_extension(f"cogs.{extension}")
        await ctx.send(f"Extension {extension} unloaded")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, extension):
        self.bot.reload_extension(f"cogs.{extension}")
        await ctx.send(f"Extension {extension} reloaded")

    # May be diff when hosted
    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send(f"Shutting Mathermind down")
        await ctx.bot.logout()


def setup(bot):
    bot.add_cog(Admin(bot))
