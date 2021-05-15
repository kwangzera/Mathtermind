import discord
from discord import Colour
from discord.ext import commands

from classes.classic_solver import ClassicSolver
from classes.repeat_solver import RepeatSolver
from classes.detective_solver import DetectiveSolver


class Gameplay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Frequently used embeds for untitled reponses
        self.valid_emb = discord.Embed(title="Success", color=Colour.green())
        self.invalid_emb = discord.Embed(title="Error", color=Colour.red())
        self.guess_emb = discord.Embed()

    async def cog_before_invoke(self, ctx):
        self.valid_emb.set_footer(text=ctx.author)
        self.invalid_emb.set_footer(text=ctx.author)
        self.guess_emb.set_footer(text=ctx.author)

    @commands.command(aliases=["g"])
    async def guess(self, ctx, *nums: int):
        """Makes a guess

        Examples:
            ;g 1        -> guesses 1
            ;g 5 6      -> guesses 5 and 6
            ;g 10 7 8 4 -> guesses 10, 7, 8 and 4
        Notes:
            ;g with repeating numbers is valid in repeat mode
        """

        if self.key(ctx) not in self.bot.games:
            self.invalid_emb.description = "User is not in a game"
            await ctx.send(embed=self.invalid_emb)
            return

        game = self.bot.games[self.key(ctx)]

        print("args", nums, type(game))

        if not game.valid_guess(nums):
            await ctx.send(embed=game.log_msg)
            return

        game.add_round(nums)
        uncert = game.game_id == 2 and game.round_number <= 4
        game.board.add_field(
            name=f"Guess {game.round_number}: `{', '.join(map(str, game.rounds[-1]))}`",
            value=f"{'❓ '*uncert}{game.matches[-1]} match{'es'*(game.matches[-1] != 1)}",
            inline=False
        )

        if game.game_over:
            await ctx.send(embed=game.game_over_msg)
            self.reset_game(ctx)
            return

        self.guess_emb.title = f"Guess {game.round_number}"
        self.guess_emb.description = f"{'Perhaps'*uncert} {game.matches[-1]} number{'s'*(game.matches[-1] != 1)} from " \
                                     f"the winning "f"combo match{'es'*(game.matches[-1] == 1)} the user's guess "
        await ctx.send(embed=self.guess_emb)

    @commands.command(aliases=["sh"])
    async def show(self, ctx):
        """Shows the full guess history of the user's current game"""

        if self.key(ctx) in self.bot.games:
            await ctx.send(embed=self.bot.games[self.key(ctx)].board)
        else:
            self.invalid_emb.description = "User is not in a game"
            await ctx.send(embed=self.invalid_emb)

    @commands.command(aliases=["lv"])
    async def leave(self, ctx):
        """Leaves the user's current game"""

        if self.key(ctx) in self.bot.games:
            self.valid_emb.description = "User left the game. Results are not saved"
            await ctx.send(embed=self.valid_emb)
            self.reset_game(ctx)
        else:
            self.invalid_emb.description = "User is not in a game"
            await ctx.send(embed=self.invalid_emb)

    @commands.command(aliases=["sv"])
    async def solve(self, ctx):
        """Lists out all the possible combos for the user's current game

        The possible combos of any gamestate for any Mathtermind game type will be listed out in sorted order if
        there are 64 or less
        """

        if self.key(ctx) not in self.bot.games:
            self.invalid_emb.description = "User is not in a game"
            await ctx.send(embed=self.invalid_emb)
            return

        game = self.bot.games[self.key(ctx)]

        if game.game_id == 0:
            solution = ClassicSolver(game.rounds, game.matches, game.verified, ctx)
        elif game.game_id == 1:
            solution = RepeatSolver(game.rounds, game.matches, game.verified, ctx)
        else:
            solution = DetectiveSolver(game.rounds, game.matches, game.verified, ctx)

        solution.solve()
        await ctx.send(embed=solution.sol_panel)

    @commands.command(aliases=["id"])
    async def identify(self, ctx, target: int):
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
            self.invalid_emb.description = "The identify command is not available for the current gamemode"
            await ctx.send(embed=self.invalid_emb)
            return

        if game.round_number < 4 or not (1 <= target <= 4):
            self.invalid_emb.description = "User can only identify guesses from 1 to 4 as a lie after the 4th guess"
            await ctx.send(embed=self.invalid_emb)
            return

        if game.found_lie:
            self.invalid_emb.description = "The identify command can only be used once per game"
            await ctx.send(embed=self.invalid_emb)
            return

        game.found_lie = True
        fields = game.board.fields
        if target == game.lie_index:
            self.valid_emb.description = f"User successfully identified the lie"
            await ctx.send(embed=self.valid_emb)

            for idx in range(4):
                name, value = fields[idx].name, fields[idx].value

                # print(itm)
                game.verified[idx] = True

                if idx == game.lie_index - 1:
                    game.matches[idx] = game.actual
                    value = f"~~{value}~~\n✅ {game.actual} match{'es'*(game.actual != 1)}"
                    game.board.set_field_at(idx, name=name, value=value, inline=False)
                else:
                    game.board.set_field_at(idx, name=name, value=f"✅ {value[1:]}", inline=False)
        # TODO confirm run restore
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
