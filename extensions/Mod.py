import discord
from discord.ext import commands

class Mod(commands.Cog):
    """Mod"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="hackban")
    @commands.has_permissions(ban_members=True)
    async def hackban(self, ctx, uId, *, reason=""):
        """Bans an user that's not in the server"""
        try:
            await ctx.guild.ban(discord.Object(id=uId), reason=reason)
        except discord.Forbidden:
            await ctx.send("Could not hackban " + uId)
        else:
            await ctx.send(uId + " was hackbanned.")

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member, *, reason=""):
        """Bans an user"""
        try:
            await ctx.guild.ban(user, reason=reason)
        except discord.Forbidden:
            await ctx.send("Could not ban " + user.name)
        else:
            await ctx.send(user.name + " was banned.")

    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, uId, *, reason=""):
        """Unbans an user"""
        # TODO: Read bans and parse using username instead of ID
        try:
            await ctx.guild.ban(discord.Object(id=uId), reason=reason)
        except discord.Forbidden:
            await ctx.send("Could not unban " + uId)
        else:
            await ctx.send(uId + " was unbanned.")

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member, *, reason=""):
        """Kicks an user"""
        try:
            await ctx.guild.kick(user, reason=reason)
        except discord.Forbidden:
            await ctx.send("Could not kick " + user.name)
        else:
            await ctx.send(user.name + " was kicked.")

    @commands.command(name="nick", aliases=["nickname"])
    @commands.has_permissions(change_nickname=True)
    async def nick(self, ctx, user: discord.Member, *, nick=""):
        """Changes user's nickname"""
        try:
            await user.edit(nick=nick)
        except discord.Forbidden:
            await ctx.send("Could not change " + user.name + "'s nickname")
        else:
            await ctx.send(user.name + "'s nickname was changed to `"+nick+"`")

    @commands.command(name="role")
    @commands.has_permissions(manage_roles=True)
    async def role(self, ctx, user: discord.Member, *, role: discord.Role):
        """Add or remove role from user"""
        if role in user.roles:
            try:
                await user.remove_roles(role)
            except discord.Forbidden:
                await ctx.send("Could not remove " + user.name + "'s role")
            else:
                await ctx.send(user.name + " was removed from the role " + role.name)
        else:
            try:
                await user.add_roles(role)
            except discord.Forbidden:
                await ctx.send("Could not add a role to " + user.name)
            else:
                await ctx.send(user.name + " was given the role " + role.name)

    @commands.command(name="createinvite", aliases=["makeinv"])
    @commands.has_permissions(create_instant_invite=True)
    async def createinvite(self, ctx, limit=0, duration_minutes=0):
        inv = await ctx.channel.create_invite(max_age=duration_minutes*60, max_uses=limit)
        info = "Invite lasts for `"+ (str(inv.max_age // 60) if inv.max_age else "∞") + "` minutes.\n" \
        + "Invite can be used `"+ (str(inv.max_uses) if inv.max_uses else "∞") + "` times."
        await ctx.send("Invite created: https://discord.gg/" + inv.code + "\n" + info)

    @commands.command(name='purge', aliases=['prune'])
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int=None):
        """Purge an amount of messages in a channel"""
        if amount>500 or amount<0:
            raise commands.CommandError(message="Invalid amount")
        await ctx.message.delete()
        await ctx.message.channel.purge(limit=amount)
        await ctx.send(f'Sucesfully deleted **{int(amount)}** messages!', delete_after=5)

    @commands.command(name='echo', aliases=['say', 'repeat'])
    @commands.has_permissions(manage_messages=True)
    async def echo(self, ctx, *message):
        await ctx.send(" ".join(message))

def setup(bot):
    bot.add_cog(Mod(bot))