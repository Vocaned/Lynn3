from discord.ext import commands
from BotUtils import splitMessage
import subprocess

class Git(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(hidden=True)
    @commands.is_owner()
    async def git(self, ctx):
        if not ctx.invoked_subcommand:
            raise commands.UserInputError()

    @git.command(name='reset', aliases=['fuck'])
    async def gitreset(self, ctx):
        p = subprocess.check_output(['git', 'reset', '--hard', 'origin/master'], stderr=subprocess.STDOUT, timeout=30).decode('utf-8')
        await ctx.send(splitMessage(p)[0])

    @git.command(name='pull')
    async def gitpull(self, ctx):
        p = subprocess.check_output(['git', 'pull'], stderr=subprocess.STDOUT, timeout=30).decode('utf-8')
        w = p.split()
        try:
            commits = w[w.index('Updating') + 1]

            p2 = subprocess.check_output(['git', 'log', '--format=%h %an | %B%n%N', commits], stderr=subprocess.STDOUT, timeout=30)
            p2 = '\n'.join([line for line in p2.decode('utf-8').split('\n') if line.strip() != ''])
        except:
            p2 = ''
        # 1993 = 2000 - len('```\n```')
        if len(p) + len(p2) >= 1993:
            if len(p) >= 1994:
                await ctx.send('Git output too long. Changes were still applied.')
            else:
                await ctx.send('```' + p + '```')
        else:
            await ctx.send('```' + p + '\n' + p2 + '```')

    @git.command(name='log', aliases=['show'])
    async def gitlog(self, ctx, last='1'):
        p = subprocess.check_output(['git', 'log', '-'+last], stderr=subprocess.STDOUT, timeout=30).decode('utf-8')
        await ctx.send('```' + p[:1994] + '```')

def setup(bot):
    bot.add_cog(Git(bot))