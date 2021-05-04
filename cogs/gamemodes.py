from discord.ext import commands

from classes.classic import Classic


class Gamemodes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Multiple users stored in bot, reload doesn't erase gamestate
        if not hasattr(bot, "games"):
            bot.games = {}
        if not hasattr(bot, "boards"):
            bot.boards = {}

        self.games = bot.games
        self.boards = bot.boards

    @commands.command(aliases=["cl"])
    async def classic(self, ctx):
        """Starts a Mathtermind game in classic mode

        7 Guesses to find winning combo, 8th Guess to determine it
        Each guess consists of 1-4 unique nubmers
        Winning combo consists of 3 unique numbers from 1-15
        """

        if self.games[ctx.author] is None:
            self.games[ctx.author] = Classic()
            self.boards[ctx.author] = f"\n{ctx.author}'s Game\n\n"
            print(self.games[ctx.author].answer)
            await ctx.send("Ready to play")

    # TODO deal with Oops, an error occurred: MissingRequiredArgument('nums is a required argument that is missing.')
    # TODO update this docstring when implemented other gamemodes
    @commands.command(aliases=["g"], require_var_positional=True)
    async def guess(self, ctx, *nums: int):
        """Makes a guess

        Examples:
            ;g 1        -> guesses 1
            ;g 5 6      -> guesses 5 and 6
            ;g 10 7 8 3 -> guesses 10, 7, 8 and 3

        Note that certain gamemodes have different restrictions on guesses
        """

        game = self.games[ctx.author]

        if game is not None:
            print("args", nums)

            if not game.valid_guess(nums):
                await ctx.send("Invalid guess bruv")
                return

            game.add_round(nums)
            guess_str = f"Guess {game.round_number}: {', '.join(map(str, game.rounds[-1]))}"
            match_str = f"{game.matches[-1]} match(es)"
            self.boards[ctx.author] += f"{guess_str}\n{match_str}\n"

            if game.game_over == 1:
                await ctx.send(f"GG {ctx.author.mention}, you won")
                self.reset_game(ctx)
                return
            elif game.game_over == 2:
                await ctx.send(f"{ctx.author.mention}, you lost. The answer was {game.answer}")
                self.reset_game(ctx)
                return

            await ctx.send(f"```{match_str}```")

    @commands.command(aliases=["sh"])
    async def show(self, ctx):
        """Shows the full guess history of a user's current game"""

        if self.games[ctx.author] is not None:
            await ctx.send(f"```{self.boards[ctx.author]}```")
        else:
            await ctx.send("User is not in a game")

    @commands.command(aliases=["lv"])
    async def leave(self, ctx):
        """Leaves a user's current game if it exists"""

        if self.games[ctx.author] is not None:
            await ctx.send("Left game")
            self.reset_game(ctx)
        else:
            await ctx.send("User is not in a game")

    async def cog_before_invoke(self, ctx):
        print("invoke", ctx.author)
        # Set to none only if doesn't exist
        self.games.setdefault(ctx.author, None)

    # TODO ;identify or smth for lie gamemode

    def reset_game(self, ctx):
        self.games[ctx.author] = None
        self.boards[ctx.author] = None


def setup(bot):
    bot.add_cog(Gamemodes(bot))
