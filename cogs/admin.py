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
        await ctx.reply(f"Extension {extension} loaded", mention_author=False)

    @commands.command(hidden=True)
    async def unload(self, ctx, extension):
        self.bot.unload_extension(f"cogs.{extension}")
        await ctx.reply(f"Extension {extension} unloaded", mention_author=False)

    @commands.command(hidden=True)
    async def reload(self, ctx, extension):
        self.bot.reload_extension(f"cogs.{extension}")
        await ctx.reply(f"Extension {extension} reloaded", mention_author=False)

    @commands.command(hidden=True)
    async def dbgame(self, ctx, user_id: int = None):
        pprint(self.bot.games[(ctx.author.id if user_id is None else user_id, ctx.guild.id)].__dict__)
        await ctx.reply("Game debug info printed in terminal", mention_author=False)

    @commands.command(hidden=True)
    async def dbstats(self, ctx, user_id: int = None):
        ...

    # May be diff when hosted
    @commands.command(hidden=True)
    async def shutdown(self, ctx):
        await ctx.reply(f"Shutting Mathermind down", mention_author=False)
        await ctx.bot.logout()


def setup(bot):
    bot.add_cog(Admin(bot))
