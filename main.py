import os
import discord
from discord.ext import commands, tasks
import ephem
from datetime import datetime, timezone
from keep_alive import keep_alive

# Keep bot alive
keep_alive()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Environment variables
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = os.environ.get('CHANNEL_ID')

# Check environment variables
if BOT_TOKEN is None:
    raise ValueError("Environment variable BOT_TOKEN is missing!")
if CHANNEL_ID is None:
    raise ValueError("Environment variable CHANNEL_ID is missing!")

CHANNEL_ID = int(CHANNEL_ID)

# Functions
def get_moon_phase():
    moon = ephem.Moon()
    moon.compute(datetime.now(timezone.utc))
    phase = moon.phase  # 0=new, 100=full
    return phase

def moon_emoji(phase):
    if phase < 1:
        return "🌑"
    elif phase < 7:
        return "🌒"
    elif phase < 14:
        return "🌓"
    elif phase < 21:
        return "🌔"
    else:
        return "🌕"

# Commands
@bot.command()
async def currentmoon(ctx):
    try:
        phase = get_moon_phase()
        emoji = moon_emoji(phase)
        await ctx.send(f"The current moon phase is: {emoji} ({phase:.1f}%)")
    except Exception as e:
        await ctx.send("❌ Something went wrong showing the Moon.")
        print(f"Error in !currentmoon command: {e}")

# Daily moon post loop
@tasks.loop(minutes=60)
async def daily_moon_post():
    try:
        now = datetime.now(timezone.utc)  # fixed timezone-aware datetime
        if now.hour == 12:
            channel = bot.get_channel(CHANNEL_ID)
            if channel:
                phase = get_moon_phase()
                emoji = moon_emoji(phase)
                await channel.send(f"🌙 Daily Moon Update: {emoji} ({phase:.1f}%)")
            else:
                print(f"Channel {CHANNEL_ID} not found!")
    except Exception as e:
        print(f"Error in daily_moon_post loop: {e}")

@daily_moon_post.before_loop
async def before_daily_moon_post():
    await bot.wait_until_ready()

# Start daily loop safely after bot is ready
@bot.event
async def on_ready():
    print(f"{bot.user} is online!")
    if not daily_moon_post.is_running():
        daily_moon_post.start()

# Run bot
bot.run(BOT_TOKEN)
