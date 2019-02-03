import discord
from discord.ext import commands
from os import listdir
from os.path import isfile, join
import sys, traceback
import config
import os



def get_prefix(bot, message):
    prefixes = ['%', 'lynn ']

    # Check to see if we are outside of a guild. e.g DM's etc.
    if not message.guild:
        # Only allow % to be used in DMs
        return '%'

    if message.guild.id == 485076757733572608:
        return '/'
    
    if message.guild.id == 336642139381301249:
        return 'lynn '

    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)


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
async def on_message(ctx):
    if ctx.author.bot or ctx.guild.id != 485076757733572608:
        await bot.process_commands(ctx)
        return
    if not os.path.exists(str(ctx.author.id)+'.dat'):
        with open(str(ctx.author.id)+'.dat', 'w') as file:
            file.write('0')
            file.close()
    with open(str(ctx.author.id)+'.dat','r') as file:
        score = int(file.read())
        file.close()
    with open(str(ctx.author.id)+'.dat','w') as file:
        file.write(str(score+1))
        file.close()
    print('Score ' + str(score+1))
    await bot.process_commands(ctx)

@bot.event
async def on_ready():
    print(f'Logged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}')

bot.run(config.token, bot=True, reconnect=True)