from contextlib import closing

import psycopg2
import discord
from discord import Colour
from discord.ext import commands


class Gamestats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.valid_emb = discord.Embed(color=Colour.green())
        self.invalid_emb = discord.Embed(color=Colour.red())

    @commands.command()
    async def initstats(self, ctx):
        with closing(self.bot.con.cursor()) as cur:
            # Check if the table exists
            cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'mtm_user');")
            exists = cur.fetchone()[0]

            # Cannot use command if already initialized
            if exists:
                await ctx.send("ur alreadi in the db bruv", author_mention=False)
                return

            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS mtm_user (
                    author_id           TEXT,
                    guild_id            TEXT,
                    game_id             INT,
                    wins                INT,
                    losses              INT,
                    longest_win_streak  INT,
                    longest_loss_streak INT,
                    current_streak      INT,
                    times_quit          INT,
                    prev_result         INT,
                    logging             BOOL,
                    PRIMARY KEY (author_id, guild_id, game_id)
                );
            """)
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS mtm_user_raw (
                    author_id TEXT,
                    guild_id  TEXT,
                    game_id   INT,
                    raw_data  TEXT,
                    PRIMARY KEY (author_id, guild_id, game_id)
                );
            """)

            for g_id in range(3):
                cur.execute(f"""
                    INSERT INTO mtm_user (author_id, guild_id, game_id, wins, losses, longest_win_streak, longest_loss_streak, current_streak, times_quit, prev_result, logging)
                    VALUES ('{ctx.author.id}', '{ctx.guild.id}', {g_id}, 0, 0, 0, 0, 0, 0, -1, f);
                """)
                cur.execute(f"""
                    INSERT INTO mtm_user_raw (author_id, guild_id, game_id, raw_data)
                    VALUES ('{ctx.author.id}', '{ctx.guild.id}', {g_id}, '');
                """)

            self.bot.con.commit()
            await ctx.reply("success, committed", mention_author=False)

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


def setup(bot):
    bot.add_cog(Gamestats(bot))
