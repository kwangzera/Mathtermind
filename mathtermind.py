import os

from discord.ext import commands

bot = commands.Bot(command_prefix=";")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    # Loading extensions on startup
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"Loaded {filename}")


# TODO figure out how it works later
@bot.event
async def on_command_error(ctx, error):
    # Unpack the error for cleaner error messages
    if isinstance(error, commands.CommandInvokeError):
        error = error.__cause__ or error

    await ctx.send(f"Oops, an error occurred: `{error!r}`")


bot.run("TOKEN")
