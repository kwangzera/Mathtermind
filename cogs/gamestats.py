import discord
from discord import Colour
from discord.ext import commands

from classes.stat_manager import StatManager


class Gamestats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.valid_emb = discord.Embed(color=Colour.green())
        self.invalid_emb = discord.Embed(color=Colour.red())
        self.neutral_emb = discord.Embed()
        self.manager = StatManager(self.bot.con)

    async def cog_check(self, ctx):
        if not self.manager.user_in_db(ctx) and str(ctx.command) != "add":
            self.invalid_emb.description = "User does not exist in the database. Enter `;add` to be added."
            await ctx.reply(embed=self.invalid_emb, mention_author=False)
            return False

        return True

    @commands.command()
    async def add(self, ctx):
        """Adds the user to the database"""
        # Cannot use command if table already initialized
        if self.manager.user_in_db(ctx):
            self.invalid_emb.description = "User already exists in the database"
            await ctx.reply(embed=self.invalid_emb, mention_author=False)
            return

        with self.bot.con.cursor() as cur:
            for gid in range(3):
                cur.execute(f"""
                    INSERT INTO mtm_user (
                        author_id,
                        guild_id,
                        game_id,
                        wins,
                        losses,
                        cur_win,
                        cur_loss,
                        longest_win_streak,
                        longest_loss_streak,
                        current_streak,
                        times_quit,
                        prev_result,
                        logging
                    ) VALUES ('{ctx.author.id}', '{ctx.guild.id}', {gid}, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'f');
                """)
                cur.execute(f"""
                    INSERT INTO mtm_user_raw (
                        author_id,
                        guild_id,
                        game_id,
                        raw_data
                    ) VALUES ('{ctx.author.id}', '{ctx.guild.id}', {gid}, '');
                """)

            self.bot.con.commit()

            self.valid_emb.description = "User has been successfully added to the database"
            await ctx.reply(embed=self.valid_emb)

    @commands.command(aliases=["lg"])
    async def logging(self, ctx, toggle: bool = None):
        """Shows the user's data logging status or toggles it on or off"""

        if toggle is None:
            cur_log = self.manager.query(ctx, 0, "logging")
            self.neutral_emb.description = f"Current logging status set to `{cur_log}`"
            await ctx.reply(embed=self.neutral_emb, mention_author=False)
            return

        self.manager.update(ctx, 0, logging=toggle)

        self.valid_emb.description = f"Successfully set logging status updated to `{toggle}`"
        await ctx.reply(embed=self.valid_emb)

    @commands.command()
    async def raw(self, ctx):
        """Outputs the user's raw game data as a .txt file"""
        ...

    @commands.command(aliases=["rs"])
    async def remove(self, ctx):
        """Removes the user from the database"""

        with self.bot.con.cursor() as cur:
            cur.execute(f"DELETE FROM mtm_user WHERE author_id = '{ctx.author.id}' AND guild_id = '{ctx.guild.id}';")
            cur.execute(f"DELETE FROM mtm_user_raw WHERE author_id = '{ctx.author.id}' AND guild_id = '{ctx.guild.id}';")

        self.valid_emb.description = "User has been successfully removed from the database"
        await ctx.reply(embed=self.valid_emb)

    @commands.command(aliases=["st"])
    async def stats(self, ctx):
        """Displays a detailed table of the user's game stats"""
        ...


def setup(bot):
    bot.add_cog(Gamestats(bot))
