import discord
from datetime import datetime
from discord.ext import commands

async def embedMsg(channel, hex, title="", description=""):
    embed = discord.Embed(title=str(title), colour=hex)
    embed.description = str(description)
    embed.timestamp = datetime.utcnow()
    return await channel.send(embed=embed, content='')