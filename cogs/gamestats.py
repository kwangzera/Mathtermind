from contextlib import closing

import discord
from discord import Colour
from discord.ext import commands
# from psycopg2.errors import DuplicateTable


class Gamestats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.valid_emb = discord.Embed(color=Colour.green())
        self.invalid_emb = discord.Embed(color=Colour.red())

        # Storing dict of users in bot, also reload doesn't erase gamestates
        # TODO hasattr another dict for stats

    @commands.command()
    async def initstats(self, ctx):
        with closing(self.bot.con.cursor()) as cur:
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.key(ctx)} (
                    game_id             INT PRIMARY KEY,
                    wins                INT,
                    losses              INT,
                    longest_win_streak  INT,
                    longest_loss_streak INT,
                    current_streak      INT,
                    times_quit          INT,
                    prev_operation      INT,
                    logging             BOOL,
                );
            """)
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.key(ctx)}r (
                    game_id  INT PRIMARY KEY,
                    raw_data TEXT,
                );
            """)
            # for gid in range(3):
            #     print(gid)
            # cur.execute(f"INSERT INTO {self.key(ctx)}")
        self.invalid_emb.description = "User is not in a game"
        await ctx.reply()
        print(type(self.bot.con))
        ...

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
        """Returns unique identification key containing user id and server id"""

        return f"{ctx.author.id}{ctx.guild.id}"


def setup(bot):
    bot.add_cog(Gamestats(bot))
