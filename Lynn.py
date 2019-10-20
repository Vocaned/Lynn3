import discord
from discord.ext import commands
import traceback
import config
import os
import logging

errors = ""
bot = commands.Bot(command_prefix=config.get_prefix, description=config.description)

if __name__ == '__main__':
    for extension in [f.replace('.py', '') for f in os.listdir("extensions") if os.path.isfile(os.path.join("extensions", f))]:
        try:
            bot.load_extension(config.cogDir + '.' + extension)
        except (discord.ClientException, ModuleNotFoundError):
            logging.error(f'Failed to load extension {extension}.', exc_info=True)

    @bot.event
    async def on_ready():
        logging.info(f'Logged in as: {bot.user.name} - {bot.user.id}')
        logging.info(f'Discord.py version: {discord.__version__}')

    @bot.event
    async def on_message(message):
        ctx = await bot.get_context(message)
        if ctx.valid:
            async with ctx.channel.typing():
                await bot.process_commands(message)

    bot.run(config.token, bot=True, reconnect=True)