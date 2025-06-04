import discord
from discord.ext import commands
from odds import get_odds, detect_arbitrage
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command(name="bestbets")
async def bestbets(ctx):
    data = get_odds()
    if isinstance(data, str):
        await ctx.send(data)
        return

    msg = "**🎯 Best Odds Today**\n\n"
    for game in data[:3]:
        teams = game["teams"]
        msg += f"**{teams[0]} vs {teams[1]}**\n"
        for book in game["bookmakers"]:
            line = book["markets"][0]["outcomes"]
            odds_str = " / ".join([f"{o['name']} @ {o['price']}" for o in line])
            msg += f"• {book['title']}: {odds_str}\n"
        msg += "\n"
    await ctx.send(msg)

@bot.command(name="arbs")
async def arbs(ctx):
    data = get_odds()
    if isinstance(data, str):
        await ctx.send(data)
        return
    arbs = detect_arbitrage(data)
    if not arbs:
        await ctx.send("😕 No arbitrage opportunities found.")
        return

    msg = "**💰 Arbitrage Opportunities**\n\n"
    for arb in arbs[:2]:
        msg += f"**{arb['teams'][0]} vs {arb['teams'][1]}**\n"
        for name, out in arb["outcomes"].items():
            msg += f"{name} @ {out['price']} ({out['book']})\n"
        msg += f"→ Profit Margin: **{arb['profit']}%**\n\n"
    await ctx.send(msg)

bot.run(TOKEN)
