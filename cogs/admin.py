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

    # May be diff when hosted
    @commands.command(hidden=True)
    async def shutdown(self, ctx):
        await ctx.send(f"Shutting Mathermind down")
        await ctx.bot.logout()

    @commands.command(hidden=True)
    async def debuginfo(self, ctx, author_id: int = None):
        if author_id is None:
            author_id = ctx.author.id

        pprint(self.bot.games[(author_id, ctx.guild.id)].__dict__)
        await ctx.send("Debug info printed in terminal")


def setup(bot):
    bot.add_cog(Admin(bot))
