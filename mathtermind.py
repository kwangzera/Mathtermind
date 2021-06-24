import os

import psycopg2
from discord.ext import commands

# Initializing bot
bot = commands.Bot(command_prefix=";")

# Initializing database
conn = psycopg2.connect(database="postgres", user="numgameadmin", password="numbergame1234", host="127.0.0.1", port="5432")
print("Database opened successfully")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    # Loading extensions on startup
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"Loaded {filename}")

    print("All extensions loaded successfully")


# Whole database connection stored in bot
if not hasattr(bot, "con"):
    bot.con = conn

# Token saved to environment variable
bot.run(os.environ["MTM_TOKEN"])
bot.con.close()
