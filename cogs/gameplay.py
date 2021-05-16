import discord
from discord import Colour
from discord.ext import commands

from classes.classic_solver import ClassicSolver
from classes.repeat_solver import RepeatSolver
from classes.detective_solver import DetectiveSolver


class Gameplay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Frequently used embeds for responses
        self.valid_emb = discord.Embed(color=Colour.green())
        self.invalid_emb = discord.Embed(color=Colour.red())

    @commands.command(aliases=["g"])
    async def guess(self, ctx, *nums: int):
        """Makes a guess

        The guess command can be used as follows for all gamemodes:
            ;g 1        -> guesses 1
            ;g 5 6      -> guesses 5 and 6
            ;g 10 7 8 4 -> guesses 10, 7, 8, and 4

        Duplicate guesses are allowed in repeat mode:
            ;g 12 5 5   -> guesses 12 once and 5 twice
            ;g 7 7 7    -> guesses 7 three times

        The bot will respond with the number of numbers from the winning combination that matches your guess. The
        following would return 1 since only the number 1 appears again in your guess.
            Winning combination: (1), 6, 7
            Your guess         : (1), 2

        For repeat mode, the following would return 2 since 2 numbers from the winning combination appears in your guess
            Winning combination: (2), 2, (9)
            Your guess         : (2), (9), 9

        In your final guess, you are only allowed to guess 3 numbers, and the game will tell you if you won
        (all 3 numbers match) or lost (not all 3 numbers match).
        """

        if self.key(ctx) not in self.bot.games:
            self.invalid_emb.description = "User is not in a game"
            await ctx.send(embed=self.invalid_emb)
            return

        game = self.bot.games[self.key(ctx)]
        uncert = game.game_id == 2 and game.round_number < 4

        if not game.valid_guess(nums):
            await ctx.send(embed=game.log_msg)
            return

        game.add_round(nums)
        game.board.add_field(
            name=f"Guess {game.round_number}: `{', '.join(map(str, game.rounds[-1]))}`",
            value=f"{'❓ '*uncert}{game.matches[-1]} match{'es'*(game.matches[-1] != 1)}",
            inline=False
        )

        if game.game_over:
            await ctx.send(embed=game.game_over_msg)
            self.reset_game(ctx)
            return

        guess_emb = discord.Embed()
        guess_emb.title = f"Guess {game.round_number}"
        guess_emb.description = f"{'Perhaps'*uncert} {game.matches[-1]} number{'s'*(game.matches[-1] != 1)} from " \
                                     f"the winning "f"combination match{'es'*(game.matches[-1] == 1)} the user's guess"
        await ctx.send(embed=guess_emb)

    @commands.command(aliases=["sh"])
    async def show(self, ctx):
        """Shows the full guess history of the user's current game

        Every single round except for the one where you make your final guess will be tabulated nicely containing the
        guess number, the sequence of numbers you guessed, and the number of matches.

        In detective mode the first 4 guesses will be preceded by a ❓ since you don't know which guess contains a
        false number of matches (the lie). Guesses (the first 4 in detective mode) where you now know the number of
        matches for certain will then be preceded by a ✅ instead.
        """

        if self.key(ctx) in self.bot.games:
            await ctx.send(embed=self.bot.games[self.key(ctx)].board)
        else:
            self.invalid_emb.description = "User is not in a game"
            await ctx.send(embed=self.invalid_emb)

    @commands.command(aliases=["lv"])
    async def leave(self, ctx):  # TODO visit ;logging
        """Leaves the user's current game

        Leaving a game does not effect your number of wins and losses. However, the number of times you leave a game may
        be logged and get negatively impact your score.
        """

        if self.key(ctx) in self.bot.games:
            self.valid_emb.description = "User successfully left the game"
            await ctx.send(embed=self.valid_emb)
            self.reset_game(ctx)
        else:
            self.invalid_emb.description = "User is not in a game"
            await ctx.send(embed=self.invalid_emb)
    # TODO combo or combination, for this change comb to sol
    @commands.command(aliases=["sv"])
    async def solve(self, ctx):
        """Lists out all the possible combinations for the user's current game

        A possible combination is a tuple of 3 numbers that could be the winning combination for a given gamestate. For
        classic and detective mode possible combinations will include (1, 2, 3) to (13, 14, 15) and for repeat mode, 
        (1, 1, 1) to (15, 15, 15).

        The possible combinations of any gamestate for any Mathtermind game type will be listed out in sorted order if
        there are 64 or less.

        In detective mode, possible combinations are generated based on verified guesses (where you are certain the 
        number of matches is true). Verified guesses includes guesses 5 to 8 and guesses 1 to 4 preceded by a ✅. All
        guesses are verified in classic and repeat mode.
        """

        if self.key(ctx) not in self.bot.games:
            self.invalid_emb.description = "User is not in a game"
            await ctx.send(embed=self.invalid_emb)
            return

        game = self.bot.games[self.key(ctx)]

        if game.game_id == 0:
            solution = ClassicSolver(game.rounds, game.matches, game.verified)
        elif game.game_id == 1:
            solution = RepeatSolver(game.rounds, game.matches, game.verified)
        else:
            solution = DetectiveSolver(game.rounds, game.matches, game.verified)

        solution.solve()
        await ctx.send(embed=solution.sol_panel)

    @commands.command(aliases=["id"])
    async def identify(self, ctx, target: int = None):
        """Identifies a lie in detective mode

        Examples:
            ;id 1 -> attempts to identify guess 1 as the lie
            ;id 4 -> attempts to identify guess 4 as the lie
        Notes:
            This command can be only used once per game
        """

        if self.key(ctx) not in self.bot.games:
            self.invalid_emb.description = "User is not in a game"
            await ctx.send(embed=self.invalid_emb)
            return

        game = self.bot.games[self.key(ctx)]

        if game.game_id != 2:
            self.invalid_emb.description = "This command is not available for the current gamemode"
            await ctx.send(embed=self.invalid_emb)
            return

        if target is None or game.round_number < 4 or not (1 <= target <= 4):
            self.invalid_emb.description = "The user can only identify one of guesses 1 to 4 as a lie only after guess 4"
            await ctx.send(embed=self.invalid_emb)
            return

        if game.found_lie:
            self.invalid_emb.description = "This command can only be used once per game"
            await ctx.send(embed=self.invalid_emb)
            return

        game.found_lie = True
        fields = game.board.fields

        if target == game.lie_index:
            self.valid_emb.description = f"User successfully identified the lie"
            await ctx.send(embed=self.valid_emb)

            for idx in range(4):
                name, value = fields[idx].name, fields[idx].value
                game.verified[idx] = True

                if idx == game.lie_index - 1:
                    game.matches[idx] = game.actual
                    value = f"~~{value}~~\n✅ {game.actual} match{'es'*(game.actual != 1)}"
                    game.board.set_field_at(idx, name=name, value=value, inline=False)
                else:
                    game.board.set_field_at(idx, name=name, value=f"✅ {value[1:]}", inline=False)

        else:
            target -= 1
            self.invalid_emb.description = "User failed to identify the lie"
            await ctx.send(embed=self.invalid_emb)

            # Know that this is right
            game.verified[target] = True
            name, value = fields[target].name, fields[target].value
            game.board.set_field_at(target, name=name, value=f"✅ {value[1:]}", inline=False)

    def reset_game(self, ctx):
        self.bot.games.pop(self.key(ctx))

    def key(self, ctx):
        """Each game is unique based on the player and the guild"""

        return ctx.author.id, ctx.guild.id


def setup(bot):
    bot.add_cog(Gameplay(bot))
