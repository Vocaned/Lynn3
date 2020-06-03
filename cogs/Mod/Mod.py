import discord
from discord.ext import commands
import aiohttp
import io

class Mod(commands.Cog):
    '''Mod'''

    def __init__(self, bot):
        self.bot = bot

    # https://github.com/Rapptz/RoboDanny/blob/ffa6657d9618131ef65c59488b9f3b9ff85e16c7/cogs/mod.py#L122
    class BannedMember(commands.Converter):
        async def convert(self, ctx, argument):
            ban_list = await ctx.guild.bans()
            try:
                member_id = int(argument, base=10)
                entity = discord.utils.find(lambda u: u.user.id == member_id, ban_list)
            except ValueError:
                entity = discord.utils.find(lambda u: str(u.user) == argument, ban_list)

            if entity is None:
                raise commands.BadArgument('%Not a valid previously-banned member.')
            return entity

    @commands.command(name='hackban')
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.guild_only()
    async def hackban(self, ctx, *, uId):
        '''Bans an user that's not in the server'''
        try:
            await ctx.guild.ban(discord.Object(id=uId), reason=f'Hackbanned by {ctx.author.name}')
        except discord.Forbidden:
            await ctx.send(f'Could not hackban {uId}')
        else:
            await ctx.send(f'{uId} was hackbanned.')

    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(self, ctx, *, user: discord.Member):
        '''Bans an user'''
        try:
            await ctx.guild.ban(user, reason=f'Banned by {ctx.author.name}')
        except discord.Forbidden:
            await ctx.send(f'Could not ban {user.name}')
        else:
            await ctx.send(f'{user.name} was banned.')

    @commands.command(name='unban')
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.guild_only()
    async def unban(self, ctx, *, user: BannedMember):
        '''Unbans an user'''
        try:
            await ctx.guild.unban(user.user, reason=f'Unbanned by {ctx.author.name}')
        except discord.Forbidden:
            await ctx.send(f'Could not unban {user.user.name}')
        else:
            await ctx.send(f'{user.user.name} was unbanned.')

    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(self, ctx, *, user: discord.Member):
        '''Kicks an user'''
        try:
            await ctx.guild.kick(user, reason=f'Kicked by {ctx.author.name}')
        except discord.Forbidden:
            await ctx.send(f'Could not kick {user.name}')
        else:
            await ctx.send(f'{user.name} was kicked.')

    @commands.command(name='nick', aliases=['nickname'])
    @commands.has_permissions(manage_nicknames=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    @commands.guild_only()
    async def nick(self, ctx, user: discord.Member, *, nick=''):
        '''Changes user's nickname'''
        try:
            await user.edit(nick=nick)
        except discord.Forbidden:
            await ctx.send(f'Could not change {user.name}\'s nickname')
        else:
            await ctx.send(f'{user.name}\'s nickname was changed to `{nick}`')

    @commands.command(name='role')
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    async def role(self, ctx, user: discord.Member, *, role: discord.Role):
        '''Add or remove role from user'''
        if role in user.roles:
            try:
                await user.remove_roles(role)
            except discord.Forbidden:
                await ctx.send(f'Could not remove {user.name}\'s role')
            else:
                await ctx.send(f'{user.name}\'s {role.name} role was removed')
        else:
            try:
                await user.add_roles(role)
            except discord.Forbidden:
                await ctx.send(f'Could not add a role to {user.name}')
            else:
                await ctx.send(f'{user.name} was given the role {role.name}')

    @commands.command(name='createinvite', aliases=['makeinv'])
    @commands.has_permissions(create_instant_invite=True)
    @commands.bot_has_permissions(create_instant_invite=True)
    @commands.guild_only()
    async def createinvite(self, ctx, limit=0, duration_minutes=0):
        inv = await ctx.channel.create_invite(max_age=duration_minutes*60, max_uses=limit)
        info = f'''Invite lasts for `{(str(inv.max_age // 60) if inv.max_age else '∞')}` minutes.
Invite can be used `{(str(inv.max_uses) if inv.max_uses else '∞')}` times.'''
        await ctx.send(f'Invite created: https://discord.gg/{inv.code}\n{info}')

    @commands.command(name='purge', aliases=['prune'])
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.guild_only()
    async def purge(self, ctx, amount: int=None):
        '''Purge an amount of messages in a channel'''
        if amount>500 or amount<0:
            raise commands.CommandError(message='Invalid amount')
        await ctx.message.delete()
        await ctx.message.channel.purge(limit=amount)
        await ctx.send(f'Sucesfully deleted **{int(amount)}** messages!', delete_after=5)

    @commands.command(name='emote', aliases=['emoji'])
    @commands.has_permissions(manage_emojis=True)
    @commands.bot_has_permissions(manage_emojis=True)
    @commands.guild_only()
    async def emote(self, ctx, *, args):
        '''Adds an emote with a specified name'''
        if ctx.message.attachments:
            emoji = await ctx.message.attachments[0].read()
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(args.split(' ')[0]) as resp:
                    if resp.status != 200:
                        raise commands.ArgumentParsingError()
                    data = io.BytesIO(await resp.read())
                    emoji = discord.File(emoji, args.split(' ')[0].split('/')[-1])

        ret = await ctx.guild.create_custom_emoji(name=args[1:], image=emoji)
        await ctx.send(f'Emote <:{ret.name}:{ret.id}> created successfully')

    @commands.command(name='echo', aliases=['say', 'repeat'])
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def echo(self, ctx, *message):
        await ctx.send(' '.join(message))

def setup(bot):
    bot.add_cog(Mod(bot))
