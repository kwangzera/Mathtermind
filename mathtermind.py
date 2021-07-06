import os
import traceback

import discord
import psycopg2
from discord import Colour
from discord.ext import commands

# Initializing bot
bot = commands.Bot(command_prefix=";")

# Initializing database
conn = psycopg2.connect(database="mathtermind", user="numgameadmin", password="numbergame1234", host="127.0.0.1", port="5432")
print("Database opened successfully")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    # Setting the bot's status
    await bot.change_presence(activity=discord.Game(name="a Guessing Game | ;help"))

    # Loading extensions on startup
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"Loaded {filename}")

    print("All extensions loaded successfully")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        return await ctx.send(embed=discord.Embed(description=f"You are on cooldown. Please try again in {error.retry_after:.2f} seconds.", color=Colour.red()))

# Whole database connection stored in bot
if not hasattr(bot, "con"):
    bot.con = conn

with bot.con.cursor() as cur:
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS mtm_user (
            author_id           TEXT,
            guild_id            TEXT,
            game_id             INT,
            wins                INT,
            losses              INT,
            cur_win             INT,
            cur_loss            INT,
            longest_win_streak  INT,
            longest_loss_streak INT,
            current_streak      INT,
            times_quit          INT,
            prev_result         INT,
            logging             BOOL,
            PRIMARY KEY (author_id, guild_id, game_id)
        );
    """)
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS mtm_user_raw (
            author_id TEXT,
            guild_id  TEXT,
            game_id   INT,
            raw_data  TEXT,
            PRIMARY KEY (author_id, guild_id, game_id)
        );
    """)
    bot.con.commit()

# Token saved to environment variable
bot.run(os.environ["MTM_TOKEN"])
bot.con.close()
