import asyncio
from math import ceil

import discord
from discord import Colour
from discord.ext import commands

from classes.classic_solver import ClassicSolver
from classes.repeat_solver import RepeatSolver
from classes.detective_solver import DetectiveSolver
from classes.custom_solver import CustomSolver
from classes.stat_manager import StatManager


class Gameplay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.manager = StatManager(self.bot.con)

    @commands.command(aliases=["g"], cooldown_after_parsing=True)
    @commands.cooldown(rate=1, per=1, type=commands.BucketType.member)
    async def guess(self, ctx, *nums: int):
        """Makes a guess

        The guess command can be used as follows:
            ;guess 1 2      → guesses 1 and 2
            ;guess 10 7 8 4 → guesses 10, 7, 8, and 4

        Duplicate guesses are allowed in repeat mode:
            ;guess 12 5 5   → guesses one 12 and two 5s
            ;guess 7 7 7    → guesses three 7s

        The bot will respond with the number of numbers from the winning combination
        that matches the user's guess. This is a one-for-one match, and can be
        visualized as follows: Imagine 2 sets of numbers, the winning combination and
        the user's guess. Numbers appearing in both sets are removed from both sets, and
        the removal process repeats until nothing can be removed. The number of pairs
        removed is the number of matches.

        After the user's final guess, the bot will respond with a win/lose message.
        """

        if self.key(ctx) not in self.bot.games:
            return await ctx.send(embed=discord.Embed(description="You are not in a game", color=Colour.red()))

        game = self.bot.games[self.key(ctx)]
        unknown = game.game_id == 2 and game.round_number < 4  # Determines if a question mark should be put in front of a guess

        if not game.valid_guess(nums):
            return await ctx.send(embed=game.log_msg)

        game.add_round(nums)
        game.board_info.append((f"Guess {game.round_number}: `{', '.join(map(str, game.rounds[-1]))}`", f"{'❓ '*unknown}{game.matches[-1]} match{'es'*(game.matches[-1] != 1)}"))

        if game.game_over:
            # Updating database unless it's custom mode
            if game.game_id == 3:
                game.game_over_msg.set_footer(text="Logging is disabled")
            if self.manager.user_in_db(ctx) and game.game_id != 3:
                if self.manager.query(ctx, 0, "logging"):
                    self.manager.calc_streak(ctx, game.game_id, game.game_over-1)  # Logging streaks, wins, losses
                    self.manager.incr_raw(ctx, game.game_id, game.game_over-1)  # Logging raw (game history binary string)
                    game.game_over_msg.set_footer(text="Logging is on")
                else:
                    game.game_over_msg.set_footer(text="Logging is off")

            self.reset_game(ctx)
            return await ctx.send(ctx.author.mention, embed=game.game_over_msg)

        guess_emb = discord.Embed()
        guess_emb.title = f"Guess {game.round_number}"
        guess_emb.description = f"{'Perhaps'*unknown} {game.matches[-1]} number{'s'*(game.matches[-1] != 1)} from the winning combination match{'es'*(game.matches[-1] == 1)} your guess"
        await ctx.send(embed=guess_emb)

    @commands.command(aliases=["id"], cooldown_after_parsing=True)
    @commands.cooldown(rate=1, per=1, type=commands.BucketType.member)
    async def identify(self, ctx, target: int = None):
        """Identifies a lie in detective mode

        The identify command can be used as follows:
            ;identify 1 → attempts to identify guess 1 as the lie
            ;identify 4 → attempts to identify guess 4 as the lie

        This detective mode exclusive command can be only used when the user has made at
        least 4 guesses, can only identify unverified guesses (those preceded by a ❓)
        to be a lie or not, and can be only used once per game.

        The bot will then tell the user if they correctly identified the lie or not. If
        the user did, guesses from 1 to 4 will all be verified and the game will cross
        out the former incorrect number of matches and replace it with the correct one.
        Otherwise, only the guess that was falsely identified as a lie could be
        verified as true.

        Unverified guesses that are verified to be true will be updated to be preceded
        by a ✅.
        """

        if self.key(ctx) not in self.bot.games:
            return await ctx.send(embed=discord.Embed(description="You are not in a game", color=Colour.red()))

        game = self.bot.games[self.key(ctx)]

        if game.game_id != 2:
            return await ctx.send(embed=discord.Embed(description="This command is not available for the current gamemode", color=Colour.red()))

        if target is None or game.round_number < 4 or not (1 <= target <= 4):
            return await ctx.send(embed=discord.Embed(description="You can only identify one of guesses 1 to 4 as a lie after making at least 4 guesses", color=Colour.red()))

        if game.used_identify:
            return await ctx.send(embed=discord.Embed(description="This command can only be used once per game", color=Colour.red()))

        game.used_identify = True
        fields = game.board.fields

        # Correctly identified the lie
        if target == game.lie_index:
            # Loop through the first 4 unverified guesses
            for idx in range(4):
                name, value = fields[idx].name, fields[idx].value
                game.verified[idx] = True  # All guesses verified now

                if idx == game.lie_index - 1:
                    game.matches[idx] = game.actual_match  # Replacing the lie with actual number of matches
                    value = f"~~{value}~~\n✅ {game.actual_match} match{'es'*(game.actual_match != 1)}"
                    game.board.set_field_at(idx, name=name, value=value, inline=False)
                else:
                    game.board.set_field_at(idx, name=name, value=f"✅ {value[1:]}", inline=False)

            return await ctx.send(embed=discord.Embed(description="You have successfully identified the lie", color=Colour.green()))

        target -= 1  # 0-indexed
        game.verified[target] = True  # Incorrectly identified lie must be a verified guess
        name, value = fields[target].name, fields[target].value
        game.board.set_field_at(target, name=name, value=f"✅ {value[1:]}", inline=False)
        await ctx.send(embed=discord.Embed(description="You have failed to identify the lie", color=Colour.red()))

    @commands.command(aliases=["if"])
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.member)
    async def info(self, ctx):
        # TODO update with custom, displaying settings
        """Displays the user's general information

        The info command displays general information regarding the user's current game
        and logging status (see ;help logging for more details) when they are available.
        """

        info_embed = discord.Embed()
        info_embed.title = f"{ctx.author}'s General Info"

        if self.key(ctx) not in self.bot.games:
            info_embed.add_field(name="Game Info", value="N/A", inline=False)
        else:
            game = self.bot.games[self.key(ctx)]
            gamemode = "Classic" if game.game_id == 0 else ("Repeat" if game.game_id == 1 else ("Detective" if game.game_id == 2 else "Custom"))
            lie_str = "" if game.game_id != 2 else f"Used Identify: **{game.used_identify}**"

            info_embed.add_field(
                name="Game Info",
                value=f"""
                   Gamemode: **{gamemode}**
                   Current Round: **{game.round_number + 1 if game.round_number != game.sets_dict["mg"] else "Final"}**
                   {lie_str}
                """,
                inline=False
            )

            # Settings displayed for only custom game
            if game.game_id == 3:
                info_embed.add_field(
                    name="Game Settings",
                    value=f"""
                        Available Rounds: **{game.sets_dict["mg"]}**
                        Numbers per Guess: **1{f" to {game.sets_dict['gsl']}"*(game.sets_dict['gsl'] != 1)}**
                        Guessing Range: **1 {f"to {game.sets_dict['rl']}" if game.sets_dict['rl'] != 1 else "Only"}**
                        Numbers in Answer: **{len(game.answer)}**
                    """,
                    inline=False
                )

        if not self.manager.user_in_db(ctx):
            info_embed.add_field(name="Other Info", value="N/A", inline=False)
        else:
            info_embed.add_field(name="Other Info", value=f"Logging: **{self.manager.query(ctx, 0, 'logging')}**", inline=False)

        await ctx.send(embed=info_embed)

    @commands.command(aliases=["lv"])
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.member)
    async def leave(self, ctx):
        """Leaves the user's current game

        The user can leave their game at any point by using this command. This will not
        effect the user's number of wins and losses. However, the number of times this
        command gets used may be logged (see ;help logging for more details).

        The user will automatically leave the game when it is finished.
        """

        if self.key(ctx) not in self.bot.games:
            return await ctx.send(embed=discord.Embed(description="You are not in a game", color=Colour.red()))

        game = self.bot.games[self.key(ctx)]
        game.game_over_msg.description = ":arrow_left: You have left the game"

        # Updating database unless it's custom mode
        if game.game_id == 3:
            game.game_over_msg.set_footer(text="Logging is disabled")
        elif self.manager.user_in_db(ctx):
            if self.manager.query(ctx, 0, "logging"):
                self.manager.increment(ctx, game.game_id, "times_quit")  # Logging times quit
                game.game_over_msg.set_footer(text="Logging is on")
            else:
                game.game_over_msg.set_footer(text="Logging is off")

        self.reset_game(ctx)
        await ctx.send(embed=game.game_over_msg)

    @commands.command(aliases=["sh"])
    @commands.cooldown(rate=1, per=1, type=commands.BucketType.member)
    async def show(self, ctx):
        """Shows the full guess history of the user's current game

        Every single round except for the one where the user makes their final guess
        will be displayed, containing the guess number, the sequence of guessed numbers,
        and the number of matches.

        In detective mode the first 4 guesses will be preceded by a ❓ since the user
        doesn't know which guess contains a false number of matches (the lie). Those
        first 4 guesses will be preceded by a ✅ instead if the user knows for certain
        the number of matches (see ;help identify for more details).

        In custom mode, it's possible to make many guesses. If that is the case, rounds
        will be displayed 10 at a time.
        """

        if self.key(ctx) not in self.bot.games:
            return await ctx.send(embed=discord.Embed(description="You are not in a game", color=Colour.red()))

        game = self.bot.games[self.key(ctx)]

        # Each page contains 10 guesses
        pages = ceil(len(game.board_info)/10)
        page_num = 0

        # Default page, pagination haven't been added
        game.gen_board(page_num, pages)
        page = await ctx.send(embed=game.board)

        # No need for pagination
        if pages <= 1:
            return

        await page.add_reaction("⏪")
        await page.add_reaction("⏩")

        while True:
            try:
                # Only the user who used this command can interact with this embed
                react, user = await self.bot.wait_for("reaction_add", timeout=2, check=lambda r, u: r.message.id == page.id and u.id == ctx.author.id and r.emoji in {"⏪", "⏩"})
            except asyncio.TimeoutError:
                game.board.set_footer(text="Page Expired")
                return await page.edit(embed=game.board)
            else:
                if react.emoji == "⏩":
                    page_num = min(page_num+1, pages-1)  # Can't go beyond the final page
                    await page.remove_reaction(react, user)
                elif react.emoji == "⏪":
                    page_num = max(page_num-1, 0)  # Can't go before page 0
                    await page.remove_reaction(react, user)

                game.gen_board(page_num,pages)
                await page.edit(embed=game.board)

    @commands.command(aliases=["sv"])
    @commands.cooldown(rate=1, per=1, type=commands.BucketType.member)
    async def solve(self, ctx):
        """Lists out all the possible solutions for the user's current game

        A possible solution consists of numbers that could be the winning combination
        for a given gamestate. For classic and detective mode, possible solutions may
        include (1, 2, 3), (1, 2, 4), (1, 2, 5), ... (13, 14, 15). For repeat mode,
        (1, 1, 1), (1, 1, 2), (1, 1, 3), ... (15, 15, 15). The possible solutions will
        not be listed out in sorted order if there are more than 64.

        In detective mode, possible solutions are generated based on verified guesses
        (where the user is certain that the number of matches is true). Verified guesses
        include guesses 5 to 8 and guesses 1 to 4 preceded by a ✅.

        In custom mode, the winning combination instead of the possible solutions will
        be shown.

        All guesses are verified in classic, repeat, and custom mode.
        """

        if self.key(ctx) not in self.bot.games:
            return await ctx.send(embed=discord.Embed(description="You are not in a game", color=Colour.red()))

        game = self.bot.games[self.key(ctx)]

        if game.game_id == 0:
            solution = ClassicSolver(game.rounds, game.matches, game.verified)
        elif game.game_id == 1:
            solution = RepeatSolver(game.rounds, game.matches, game.verified)
        elif game.game_id == 2:
            solution = DetectiveSolver(game.rounds, game.matches, game.verified)
        else:  # Custom game
            solution = CustomSolver(game.rounds, game.matches, game.verified, game.answer)

        solution.solve()
        await ctx.send(embed=solution.sol_panel)

    def reset_game(self, ctx):
        self.bot.games.pop(self.key(ctx))  # Removes the user's key from the dictionary

    def key(self, ctx):
        return f"{ctx.author.id}{ctx.guild.id}"


def setup(bot):
    bot.add_cog(Gameplay(bot))
