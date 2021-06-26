from contextlib import closing

import discord
from discord import Colour
from discord.ext import commands

from classes.stat_manager import StatManager


class Gamestats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.valid_emb = discord.Embed(color=Colour.green())
        self.invalid_emb = discord.Embed(color=Colour.red())
        self.manager = StatManager(self.bot.con)

    @commands.command()
    async def initstats(self, ctx):
        # Cannot use command if table already initialized
        if self.manager.table_exists(ctx):
            self.invalid_emb.description = "User already exists in the database"
            await ctx.reply(embed=self.invalid_emb, mention_author=False)
            return

        with closing(self.bot.con.cursor()) as cur:
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

            for game_id in range(3):
                cur.execute(f"""
                    INSERT INTO mtm_user (
                        author_id,
                        guild_id,
                        game_id,
                        wins,
                        losses,
                        longest_win_streak,
                        longest_loss_streak,
                        current_streak,
                        times_quit,
                        prev_result,
                        logging
                    ) VALUES ('{ctx.author.id}', '{ctx.guild.id}', {game_id}, 0, 0, 0, 0, 0, 0, -1, 'f');
                """)
                cur.execute(f"""
                    INSERT INTO mtm_user_raw (
                        author_id,
                        guild_id,
                        game_id,
                        raw_data
                    ) VALUES ('{ctx.author.id}', '{ctx.guild.id}', {game_id}, '');
                """)

            self.bot.con.commit()

            self.valid_emb.description = "User has been successfully added to the database"
            await ctx.reply(embed=self.valid_emb)

    @commands.command(aliases=["lg"])
    async def logging(self, ctx, toggle: bool = None):
        """Toggles user's data logging status on or off"""

        if toggle is None:
            self.invalid_emb.description = "Please input a boolean value"
            await ctx.reply(embed=self.invalid_emb, mention_author=False)
            return

        if not self.manager.toggle_log(ctx, toggle):
            self.invalid_emb.description = "User does not exist in the database"
            await ctx.reply(embed=self.invalid_emb, mention_author=False)
            return

        self.manager.update_log_status(ctx, toggle)

        self.valid_emb.description = f"Logging status updated to `{toggle}`"
        await ctx.reply(embed=self.valid_emb)

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
