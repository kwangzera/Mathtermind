import asyncio
import discord
from discord import Colour
from discord.ext import commands

from classes.stat_manager import StatManager

class Gamestats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stat_emb = discord.Embed()
        self.manager = StatManager(self.bot.con)

    @commands.command()
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.member)
    async def add(self, ctx):
        """Adds the user to the database

        For a user's data to be logged, they first have to be added to the database.
        Each user will be uniquely identified by their id and the id of the server they
        are currently in.
        """

        # Cannot use command if table already initialized
        if self.manager.user_in_db(ctx):
            return await ctx.send(embed=discord.Embed(description="You already exist in the database", color=Colour.red()))

        with self.bot.con.cursor() as cur:
            for game_id in range(3):
                sql = f"""
                    INSERT INTO mtm_user (
                        author_id,
                        guild_id,
                        game_id, wins,
                        losses,
                        cur_win,
                        cur_loss,
                        longest_win_streak,
                        longest_loss_streak,
                        current_streak,
                        times_quit,
                        prev_result,
                        logging
                    ) VALUES ({', '.join('%s' for _ in range(13))})"""
                data = (str(ctx.author.id), str(ctx.guild.id), game_id, 0, 0, 0, 0, 0, 0, 0, 0, 0, 'f')
                cur.execute(sql, data)

                sql_r = """
                    INSERT INTO mtm_user_raw (
                        author_id,
                        guild_id,
                        game_id,
                        raw_data
                    ) VALUES (%s, %s, %s, %s);"""
                data_r = (str(ctx.author.id), str(ctx.guild.id), game_id, '')
                cur.execute(sql_r, data_r)

                self.bot.con.commit()

        await ctx.send(ctx.author.mention, embed=discord.Embed(description="You have been successfully added to the database", color=Colour.green()))

    @commands.command(aliases=["lg"], cooldown_after_parsing=True)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.member)
    async def logging(self, ctx, toggle: bool = None):
        """Shows the user's data logging status or toggles it on or off

        The logging command can be used as follows:
            ;logging       -> shows current logging status
            ;logging True  -> turns on logging
            ;logging False -> turns off logging.

        The value for toggle can be any boolean value supported by PostgreSQL. Some
        examples include "1", "0", "on", "off", "t", "f", "yes", and "no".

        If the user has logging turned on, the number of times they leave a game will be
        logged if they decide to end a game early. Additionally, information about wins
        and losses will be logged if they finish the game. Nothing will be logged if the
        user has logging turned off.

        This command requires the user to be added to the database first.
        """

        if not self.manager.user_in_db(ctx):
            return await ctx.send(embed=discord.Embed(description="You do not exist in the database. Enter `;add` to be added.", color=Colour.red()))

        if toggle is None:
            cur_log = self.manager.query(ctx, 0, "logging")
            return await ctx.send(embed=discord.Embed(description=f"Current logging status set to `{cur_log}`"))

        self.manager.update(ctx, 0, logging=toggle)
        await ctx.send(ctx.author.mention, embed=discord.Embed(description=f"Successfully set logging status to `{toggle}`", color=Colour.green()))

    @commands.command(cooldown_after_parsing=True)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.member)
    async def raw(self, ctx, gamemode: str = None):
        """Outputs the user's raw game data of any gamemode as a .txt file

        The logging command can be used as follows:
            ;raw classic -> outputs raw data as classic.txt
            ;raw cl      -> outputs raw data as classic.txt
            ;raw repeat  -> outputs raw data as repeat.txt

        Raw game data is also the user's full game history, a binary string consisting
        of 1s (wins) and 0s (losses). The values for gamemode are the same values that
        are used to start a game.

        This command requires the user to be added to the database first.
        """

        if not self.manager.user_in_db(ctx):
            return await ctx.send(embed=discord.Embed(description="You do not exist in the database. Enter `;add` to be added.", color=Colour.red()))

        if gamemode in {"classic", "cl"}:
            await self.gen_file(ctx, 0, "classic")
        elif gamemode in {"repeat", "rp"}:
            await self.gen_file(ctx, 1, "repeat")
        elif gamemode in {"detective", "lie"}:
            await self.gen_file(ctx, 2, "detective")
        else:
            await ctx.send(embed=discord.Embed(description="Please input the name of a proper gamemode for raw file generation", color=Colour.red()))

    @commands.command(aliases=["rm"])
    @commands.cooldown(rate=1, per=10, type=commands.BucketType.member)
    async def remove(self, ctx):
        """Removes the user from the database

        When the user is removed from the database, all of their game data gets deleted.
        The ;add command must be used again if the user wants to be readded the
        database.

        Upon using this command, A message will show up to confirming if the user would
        like to wipe their game data. If the user doesn't respond within 60 seconds,
        their information will not be removed.

        This command requires the user to be added to the database first.
        """

        if not self.manager.user_in_db(ctx):
            return await ctx.send(embed=discord.Embed(description="You do not exist in the database. Enter `;add` to be added.", color=Colour.red()))

        # Special confirmation embed
        confirm = await ctx.send(ctx.author.mention, embed=discord.Embed(description="Remove yourself from the database? This action cannot be undone and will erase your game data.", color=Colour.gold()))
        await confirm.add_reaction("✅")
        await confirm.add_reaction("❌")

        try:
            react, user = await self.bot.wait_for("reaction_add", timeout=60, check=lambda r, u: r.message.id == confirm.id and u.id == ctx.author.id and r.emoji in {"✅", "❌"})
        except asyncio.TimeoutError:
            # When user does ;rm more than once when database exists
            if not self.manager.user_in_db(ctx):
                return

            await confirm.clear_reactions()
            return await confirm.edit(embed=discord.Embed(description="Confirmation timed out. You have not been removed from the database.", color=Colour.red()))
        else:
            # When user does ;rm more than once when database exists
            if not self.manager.user_in_db(ctx):
                return

            if react.emoji == "❌":
                await confirm.clear_reactions()
                return await confirm.edit(embed=discord.Embed(description="You have not been removed from the database", color=Colour.red()))

            with self.bot.con.cursor() as cur:
                cur.execute(f"DELETE FROM mtm_user WHERE author_id = '{ctx.author.id}' AND guild_id = '{ctx.guild.id}';")
                cur.execute(f"DELETE FROM mtm_user_raw WHERE author_id = '{ctx.author.id}' AND guild_id = '{ctx.guild.id}';")
                self.bot.con.commit()

            await confirm.clear_reactions()
            return await confirm.edit(embed=discord.Embed(description="You have been successfully removed from the database", color=Colour.green()))

    @commands.command(aliases=["st"])
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.member)
    async def stats(self, ctx):
        """Displays a detailed table of the user's game stats

        The stats command is used to show tabulated game data for all 3 gamemodes, which
        contain information about wins/losses, streaks, and more. The tables are
        paginated by gamemode and will expire after 60 seconds.

        This command requires the user to be added to the database first.
        """

        if not self.manager.user_in_db(ctx):
            return await ctx.send(embed=discord.Embed(description="You do not exist in the database. Enter `;add` to be added.", color=Colour.red()))

        page_num = 0
        self.gen_page(ctx, 0, "Classic")

        page = await ctx.send(ctx.author.mention, embed=self.stat_emb)
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

                await page.edit(embed=self.stat_emb)

    async def gen_file(self, ctx, game_id, gamemode):
        with open(f"{gamemode}.txt", "w") as f:
            f.write(self.manager.query_raw(ctx, game_id))

        with open(f"{gamemode}.txt", "rb") as f:
            await ctx.send(ctx.author.mention, file=discord.File(f, f"{gamemode}.txt"))

    def gen_page(self, ctx, game_id, gamemode):
        self.stat_emb.title = f"{ctx.author}'s {gamemode} Stats"
        self.stat_emb.set_footer(text=f"Page {game_id+1}/3")
        self.stat_emb.clear_fields()

        # Group 1, basic
        wins = self.manager.query(ctx, game_id, "wins")
        losses = self.manager.query(ctx, game_id, "losses")
        total = wins+losses
        win_rate = wins/total if total != 0 else 0

        # Group 2, streaks
        longest_win_streak = self.manager.query(ctx, game_id, "longest_win_streak")
        longest_loss_streak = self.manager.query(ctx, game_id, "longest_loss_streak")
        current_streak = self.manager.query(ctx, game_id, "current_streak")
        prev_result = self.manager.query(ctx, game_id, "prev_result")
        current_streak_type = f"Win{'s'*(current_streak != 1)}" if prev_result else f"Loss{'es'*(current_streak != 1)}"

        # Group 3, misc
        quits = self.manager.query(ctx, game_id, "times_quit")

        self.stat_emb.add_field(
            name=f"Basic Info",
            value=f"""
                Total Games: **{total}**
                Wins: **{wins}**
                Losses: **{losses}**
                Win Rate: **{win_rate*100:0.1f}%**
            """,
            inline=False
        )
        self.stat_emb.add_field(
            name=f"Streak Info",
            value=f"""
                Longest Win Streak: **{longest_win_streak}**
                Longest Loss Streak: **{longest_loss_streak}**
                Current Streak: **{current_streak} {current_streak_type}**
            """,
            inline=False
        )
        self.stat_emb.add_field(
            name=f"Misc Info",
            value=f"""Times Quit: **{quits}**""",
            inline=False
        )


def setup(bot):
    bot.add_cog(Gamestats(bot))
