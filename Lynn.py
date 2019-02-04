import discord
from discord.ext import commands
from os import listdir
from os.path import isfile, join
import sys, traceback
import config
import os



def get_prefix(bot, message):
    config.get_prefix(bot, message)

cogs_dir = 'extensions'
bot = commands.Bot(command_prefix=get_prefix, description='Lynn 3.0_DEV')

if __name__ == '__main__':
    for extension in [f.replace('.py', '') for f in listdir(cogs_dir) if isfile(join(cogs_dir, f))]:
        try:
            bot.load_extension(cogs_dir + '.' + extension)
        except (discord.ClientException, ModuleNotFoundError):
            print(f'Failed to load extension {extension}.')
            traceback.print_exc()

@bot.event
async def on_ready():
    print(f'Logged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}')

bot.run(config.token, bot=True, reconnect=True)