from pprint import pprint

from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.command(hidden=True)
    async def load(self, ctx, extension):
        self.bot.load_extension(f"cogs.{extension}")
        await ctx.send(f"Extension {extension} loaded")

    @commands.command(hidden=True)
    async def unload(self, ctx, extension):
        self.bot.unload_extension(f"cogs.{extension}")
        await ctx.send(f"Extension {extension} unloaded")

    @commands.command(hidden=True)
    async def reload(self, ctx, extension):
        self.bot.reload_extension(f"cogs.{extension}")
        await ctx.send(f"Extension {extension} reloaded")

    @commands.command(hidden=True)
    async def debug(self, ctx, user_id: int = None):
        if user_id is None:
            user_id = ctx.author.id

        pprint(self.bot.games[(user_id, ctx.guild.id)].__dict__)
        await ctx.send("Debug info printed in terminal")

    # May be diff when hosted
    @commands.command(hidden=True)
    async def shutdown(self, ctx):
        await ctx.send(f"Shutting Mathermind down")
        await ctx.bot.logout()


def setup(bot):
    bot.add_cog(Admin(bot))
