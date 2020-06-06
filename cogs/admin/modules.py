from discord.ext import commands
import glob

class Modules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def modules(self, ctx):
        """Lists all loaded modules"""
        modulelist = list(map(lambda x: x.replace('cogs.', ''), self.bot.extensions))
        modulelist.sort()
        await ctx.send("Loaded modules: ```" + "\n".join(modulelist) + "```")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *, module):
        """Loads a module."""
        try:
            self.bot.load_extension('cogs.'+module)
        except:
            raise commands.ExtensionNotFound(module, None)
        await ctx.send('Loaded '+module)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, module):
        """Unloads a module."""
        try:
            self.bot.unload_extension('cogs.'+module)
        except:
            raise commands.ExtensionNotFound(module, None)
        await ctx.send('Unloaded '+module)

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def _reload(self, ctx, *, module):
        """Reloads a module.
        Module can be \"all\""""
        if module == "all":
            n = 0
            loaded = self.bot.extensions
            modules = [f.replace('.py', '').replace('/', '.') for f in glob.glob('cogs/**/*.py', recursive=True)]
            for module in modules:
                if not module in loaded:
                    continue
                self.bot.reload_extension(module)
                n+=1
            await ctx.send(f'Reloaded {str(n)} modules')
        else:
            self.bot.reload_extension('cogs.'+module)
            await ctx.send('Reloaded '+str(module))

def setup(bot):
    bot.add_cog(Modules(bot))