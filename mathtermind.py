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

    print("All extensions loaded successfully")

# Token saved to environment variable
bot.run(os.environ["MTM_TOKEN"])
