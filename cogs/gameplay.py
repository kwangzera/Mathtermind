import discord
from discord import Colour
from discord.ext import commands

from classes.classic_solver import ClassicSolver
from classes.repeat_solver import RepeatSolver
from classes.detective_solver import DetectiveSolver
from classes.stat_manager import StatManager

class Gameplay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.manager = StatManager(self.bot.con)

    @commands.command(aliases=["g"])
    async def guess(self, ctx, *nums: int):
        """Makes a guess

        The guess command can be used as follows for all gamemodes:
            ;guess 1 2      -> guesses 1 and 2
            ;guess 10 7 8 4 -> guesses 10, 7, 8, and 4

        Duplicate guesses are allowed in repeat mode:
            ;guess 12 5 5   -> guesses one 12 and two 5s
            ;guess 7 7 7    -> guesses three 7s

        The bot will respond with the number of numbers from the winning combination
        that matches the user's guess. This is a one-for-one match, and can be
        visualized as follows: Imagine 2 sets of numbers, the winning combination and
        the user's guess. Numbers appearing in both sets are removed from both sets, and
        the removal process repeats until nothing can be removed. The number of pairs
        removed is the number of matches.

        After the user's final guess, the bot will respond with a win/lose message.
        """

        if self.key(ctx) not in self.bot.games:
            return await ctx.reply(embed=discord.Embed(description="You are not in a game", color=Colour.red()), mention_author=False)

        game = self.bot.games[self.key(ctx)]
        uncert = game.game_id == 2 and game.round_number < 4

        if not game.valid_guess(nums):
            return await ctx.reply(embed=game.log_msg, mention_author=False)

        game.add_round(nums)
        game.board.add_field(
            name=f"Guess {game.round_number}: `{', '.join(map(str, game.rounds[-1]))}`",
            value=f"{'❓ '*uncert}{game.matches[-1]} match{'es'*(game.matches[-1] != 1)}",
            inline=False
        )

        if game.game_over:
            # Updating database
            if self.manager.user_in_db(ctx):
                if self.manager.query(ctx, 0, "logging"):
                    self.manager.calc_streak(ctx, game.game_id, game.game_over-1)
                    self.manager.incr_raw(ctx, game.game_id, game.game_over-1)
                    game.game_over_msg.set_footer(text="Logging is on")
                else:
                    game.game_over_msg.set_footer(text="Logging is off")

            self.reset_game(ctx)
            return await ctx.reply(embed=game.game_over_msg)

        guess_emb = discord.Embed()  # TODO send embed directly or init first
        guess_emb.title = f"Guess {game.round_number}"
        guess_emb.description = f"{'Perhaps'*uncert} {game.matches[-1]} number{'s'*(game.matches[-1] != 1)} from the winning combination match{'es'*(game.matches[-1] == 1)} your guess"
        await ctx.reply(embed=guess_emb, mention_author=False)

    @commands.command(aliases=["id"])
    async def identify(self, ctx, target: int = None):
        """Identifies a lie in detective mode

        The identify command can be used as follows:
            ;identify 1 -> attempts to identify guess 1 as the lie
            ;identify 4 -> attempts to identify guess 4 as the lie

        This detective mode exclusive command can be only used when the user has made at
        least 4 guesses, can only identify unverified guesses (those preceded by a ❓)
        to be a lie or not, and can be only used once per game.

        The bot will then tell you if you correctly identified the lie or not. If you
        did, guesses from 1 to 4 will all be verified and the game will cross out the
        former incorrect number of matches and replace it with the correct one.
        Otherwise, only the guess that was falsely identified as a lie could be
        verified as true.

        Unverified guesses that are verified to be true will be updated to be preceded
        by a ✅.
        """

        if self.key(ctx) not in self.bot.games:
            return await ctx.reply(embed=discord.Embed(description="You are not in a game", color=Colour.red()), mention_author=False)

        game = self.bot.games[self.key(ctx)]

        if game.game_id != 2:
            return await ctx.reply(embed=discord.Embed(description="This command is not available for the current gamemode", color=Colour.red()), mention_author=False)

        if target is None or game.round_number < 4 or not (1 <= target <= 4):
            return await ctx.reply(embed=discord.Embed(description="You can only identify one of guesses 1 to 4 as a lie after making at least 4 guesses", color=Colour.red()), mention_author=False)

        if game.used_identify:
            return await ctx.reply(embed=discord.Embed(description="This command can only be used once per game", color=Colour.red()), mention_author=False)

        game.used_identify = True
        fields = game.board.fields

        if target == game.lie_index:
            await ctx.reply(embed=discord.Embed(description="You have successfully identified the lie", color=Colour.green()), mention_author=False)

            for idx in range(4):
                name, value = fields[idx].name, fields[idx].value
                game.verified[idx] = True

                if idx == game.lie_index - 1:
                    game.matches[idx] = game.actual_match
                    value = f"~~{value}~~\n✅ {game.actual_match} match{'es'*(game.actual_match != 1)}"
                    game.board.set_field_at(idx, name=name, value=value, inline=False)
                else:
                    game.board.set_field_at(idx, name=name, value=f"✅ {value[1:]}", inline=False)

        else:
            target -= 1
            await ctx.reply(embed=discord.Embed(description="You have failed to identify the lie", color=Colour.red()), mention_author=False)

            # Know that this is right
            game.verified[target] = True
            name, value = fields[target].name, fields[target].value
            game.board.set_field_at(target, name=name, value=f"✅ {value[1:]}", inline=False)

    @commands.command(aliases=["lv"])
    async def leave(self, ctx):
        """Leaves the user's current game

        Leaving a game will not effect the user's number of wins and losses. However,
        the number of times the user leaves a game may be logged, thus negatively
        impacting the user's score.

        The user will automatically leave the game when it is finished.
        """

        if self.key(ctx) in self.bot.games:
            game = self.bot.games[self.key(ctx)]
            game.game_over_msg.description = ":arrow_left: You have left the game"

            # Updating database
            if self.manager.user_in_db(ctx):
                if self.manager.query(ctx, 0, "logging"):
                    gid = self.bot.games[self.key(ctx)].game_id
                    self.manager.increment(ctx, gid, "times_quit")
                    game.game_over_msg.set_footer(text="Logging is on")
                else:
                    game.game_over_msg.set_footer(text="Logging is off")

            await ctx.reply(embed=game.game_over_msg)
            self.reset_game(ctx)
        else:
            await ctx.reply(embed=discord.Embed(description="You are not in a game", color=Colour.red()), mention_author=False)

    @commands.command(aliases=["sh"])
    async def show(self, ctx):
        """Shows the full guess history of the user's current game

        Every single round except for the one where the user makes their final guess
        will be displayed, containing the guess number, the sequence of guessed numbers,
        and the number of matches.

        In detective mode the first 4 guesses will be preceded by a ❓ since the user
        doesn't know which guess contains a false number of matches (the lie). Those
        first 4 guesses will be preceded by a ✅ instead if the user knows for certain
        the number of matches (see ;help id for more details).
        """

        if self.key(ctx) in self.bot.games:
            await ctx.reply(embed=self.bot.games[self.key(ctx)].board, mention_author=False)
        else:
            await ctx.reply(embed=self.discord.Embed(description="You are not in a game", color=Colour.red()), mention_author=False)

    @commands.command(aliases=["sv"])
    async def solve(self, ctx):
        """Lists out all the possible solutions for the user's current game

        A possible solution consists of 3 numbers that could be the winning combination
        for a given gamestate. For classic and detective mode, possible solutions may
        include (1, 2, 3), (1, 2, 4), (1, 2, 5), ... (13, 14, 15). For repeat mode,
        (1, 1, 1), (1, 1, 2), (1, 1, 3), ... (15, 15, 15). The possible solutions will
        not be listed out in sorted order if there are more than 64.

        In detective mode, possible solutions are generated based on verified guesses
        (where the user is certain that the number of matches is true). Verified guesses
        include guesses 5 to 8 and guesses 1 to 4 preceded by a ✅.

        All guesses are verified in classic and repeat mode.
        """

        if self.key(ctx) not in self.bot.games:
            return await ctx.reply(embed=discord.Embed(description="You are not in a game", color=Colour.red()), mention_author=False)

        game = self.bot.games[self.key(ctx)]

        if game.game_id == 0:
            solution = ClassicSolver(game.rounds, game.matches, game.verified)
        elif game.game_id == 1:
            solution = RepeatSolver(game.rounds, game.matches, game.verified)
        else:
            solution = DetectiveSolver(game.rounds, game.matches, game.verified)

        solution.solve()
        await ctx.reply(embed=solution.sol_panel, mention_author=False)

    def reset_game(self, ctx):
        self.bot.games.pop(self.key(ctx))

    def key(self, ctx):
        """Returns unique identification key containing user id and server id"""

        return f"{ctx.author.id}{ctx.guild.id}"


def setup(bot):
    bot.add_cog(Gameplay(bot))
