import discord
from discord.ext import commands
from os import listdir
from os.path import isfile, join
import sys, traceback
import config
import os
import logging

errors = ""
bot = commands.Bot(command_prefix=config.get_prefix, description=config.description)

if __name__ == '__main__':
    for extension in [f.replace('.py', '') for f in listdir(config.cogDir) if isfile(join(config.cogDir, f))]:
        try:
            bot.load_extension(config.cogDir + '.' + extension)
        except (discord.ClientException, ModuleNotFoundError):
            logging.error(f'Failed to load extension {extension}.', exc_info=True)

    @bot.event
    async def on_ready():
        logging.info(f'Logged in as: {bot.user.name} - {bot.user.id}')
        logging.info(f'Discord.py version: {discord.__version__}')

    bot.run(config.token, bot=True, reconnect=True)