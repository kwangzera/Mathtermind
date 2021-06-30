import asyncio
import discord
from discord import Colour
from discord.ext import commands

from classes.stat_manager import StatManager

class Gamestats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.valid_emb = discord.Embed(color=Colour.green())
        self.invalid_emb = discord.Embed(color=Colour.red())
        self.confirm_emb = discord.Embed(color=Colour.gold())
        self.neutral_emb = discord.Embed()

        self.manager = StatManager(self.bot.con)
        self.rm_flag = False

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
                sql = f"INSERT INTO mtm_user (author_id, guild_id, game_id, wins, losses, cur_win, cur_loss, longest_win_streak, longest_loss_streak, current_streak, times_quit, prev_result, logging)\
                        VALUES ({', '.join('%s' for _ in range(13))})"
                data = (str(ctx.author.id), str(ctx.guild.id), gid, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'f')
                cur.execute(sql, data)

                sql_r = "INSERT INTO mtm_user_raw (author_id, guild_id, game_id, raw_data) VALUES (%s, %s, %s, %s);"
                data_r = (str(ctx.author.id), str(ctx.guild.id), gid, '')
                cur.execute(sql_r, data_r)

            self.bot.con.commit()

            self.valid_emb.description = "User has been successfully added to the database"
            await ctx.reply(embed=self.valid_emb)

    @commands.command(aliases=["lg"])
    async def logging(self, ctx, toggle: bool = None):
        """Shows the user's data logging status or toggles it on or off"""

        self.neutral_emb = discord.Embed()

        if toggle is None:
            cur_log = self.manager.query(ctx, 0, "logging")
            self.neutral_emb.description = f"Current logging status set to `{cur_log}`"
            await ctx.reply(embed=self.neutral_emb, mention_author=False)
            return

        self.manager.update(ctx, 0, logging=toggle)

        self.valid_emb.description = f"Successfully set logging status to `{toggle}`"
        await ctx.reply(embed=self.valid_emb)

    @commands.command()
    async def raw(self, ctx, gmode: str = None):
        """Outputs the user's raw game data of any gamemode as a .txt file"""

        if gmode in {"classic", "cl"}:
            await self.gen_file(ctx, 0, "classic")
        elif gmode in {"repeat", "rp"}:
            await self.gen_file(ctx, 1, "repeat")
        elif gmode in {"detective", "lie"}:
            await self.gen_file(ctx, 2, "detective")
        else:
            self.invalid_emb.description = "Please input the name of a proper gamemode for raw file generation"
            await ctx.reply(embed=self.invalid_emb, mention_author=False)

    @commands.command(aliases=["rm"])
    async def remove(self, ctx):
        """Removes the user from the database"""

        # Special confirmation embed
        self.confirm_emb = discord.Embed(color=Colour.gold())
        self.confirm_emb.description = "Remove user from the database? This action cannot be undone and will erase all user data."
        confirm = await ctx.reply(embed=self.confirm_emb, mention_author=False)
        await confirm.add_reaction("✅")
        await confirm.add_reaction("❌")

        try:
            react, user = await self.bot.wait_for("reaction_add", timeout=60, check=lambda r, u: r.message.id == confirm.id and u.id == ctx.author.id and r.emoji in {"✅", "❌"})
        except asyncio.TimeoutError:
            # When user does ;rm more than once when database exists
            if not self.manager.user_in_db(ctx):
                return

            self.invalid_emb.description = "Confirmation timed out. User was not removed from the database."
            await ctx.reply(embed=self.invalid_emb)
        else:
            # When user does ;rm more than once when database exists
            if not self.manager.user_in_db(ctx):
                return

            if react.emoji == "❌":
                self.invalid_emb.description = "User has not been successfully removed from the database"
                await ctx.reply(embed=self.invalid_emb)
                return

            with self.bot.con.cursor() as cur:
                cur.execute(f"DELETE FROM mtm_user WHERE author_id = '{ctx.author.id}' AND guild_id = '{ctx.guild.id}';")
                cur.execute(f"DELETE FROM mtm_user_raw WHERE author_id = '{ctx.author.id}' AND guild_id = '{ctx.guild.id}';")

            self.valid_emb.description = "User has been successfully removed from the database"
            self.bot.con.commit()

            await ctx.reply(embed=self.valid_emb)

    @commands.command(aliases=["st"])
    async def stats(self, ctx):
        """Displays a detailed table of the user's game stats"""

        page_num = 0
        self.gen_page(ctx, 0, "Classic")
        page =  await ctx.reply(embed=self.neutral_emb, mention_author=False)
        await page.add_reaction("⏪")
        await page.add_reaction("⏩")

        while True:
            try:
                react, user = await self.bot.wait_for("reaction_add", timeout=60, check=lambda r, u: r.message.id == page.id and u.id == ctx.author.id and r.emoji in {"⏪", "⏩"})
            except asyncio.TimeoutError:
                return
            else:
                if react.emoji == "⏩":
                    page_num = min(page_num+1, 2)
                    await page.remove_reaction(react, user)
                elif react.emoji == "⏪":
                    page_num = max(page_num-1, 0)
                    await page.remove_reaction(react, user)

                if page_num == 0:
                    self.gen_page(ctx, 0, "Classic")
                elif page_num == 1:
                    self.gen_page(ctx, 1, "Repeat")
                elif page_num == 2:
                    self.gen_page(ctx, 2, "Detective")

                await page.edit(embed=self.neutral_emb)

    async def gen_file(self, ctx, game_id, filename):
        with open(f"{filename}.txt", "w") as f:
            f.write(self.manager.query_raw(ctx, game_id))

        with open(f"{filename}.txt", "rb") as f:
            await ctx.reply(file=discord.File(f, f"{filename}.txt"))

    def gen_page(self, ctx, gid, gamemode):
        self.neutral_emb.title = f"{ctx.author.name}'s {gamemode} Stats"
        self.neutral_emb.set_footer(text=f"Page {gid+1}/3")
        self.neutral_emb.clear_fields()

        # Group 1, basic
        wins = self.manager.query(ctx, gid, "wins")
        losses = self.manager.query(ctx, gid, "losses")
        total = wins+losses
        winrate = wins/total if total != 0 else 0

        # Group 2, streaks
        long_w_strk = self.manager.query(ctx, gid, "longest_win_streak")
        long_l_strk = self.manager.query(ctx, gid, "longest_loss_streak")
        cur_strk = self.manager.query(ctx, gid, "current_streak")
        pre_res = self.manager.query(ctx, gid, "prev_result")
        cur_strk_type = f"Win{'s'*(cur_strk != 1)}" if pre_res else f"Loss{'es'*(cur_strk != 1)}"

        # Group 3, misc
        quits = self.manager.query(ctx, gid, "times_quit")

        self.neutral_emb.add_field(
            name = f"Basic Info",
            value = f"""
                Total Games: `{total}`
                Wins: `{wins}`
                Losses: `{losses}`
                Win Rate: `{winrate*100:0.1f}%`
            """,
            inline=False
        )
        self.neutral_emb.add_field(
            name = f"Streak Info",
            value = f"""
                Longest Win Streak: `{long_w_strk}`
                Longest Loss Streak: `{long_l_strk}`
                Current Streak: `{cur_strk} {cur_strk_type}`
            """,
            inline=False
        )
        self.neutral_emb.add_field(
            name = f"Misc Info",
            value = f"""Times Quit: `{quits}`""",
            inline=False
        )

def setup(bot):
    bot.add_cog(Gamestats(bot))
