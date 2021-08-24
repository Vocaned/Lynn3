from discord.ext import commands
import discord

class Guild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='guild', aliases=['discord', 'invite'])
    async def DiscordAPI(self, ctx, *, invite):
        """Gets information about discord invites"""
        invite = await self.bot.fetch_invite(invite, with_counts=True)

        embed = discord.Embed(title='Click here to join the server', colour=0x7289DA, url=invite.url)
        embed.add_field(name='Guild Name', value=invite.guild.name)
        if invite.guild.description:
            embed.add_field(name='Description', value=invite.guild.description)
        embed.add_field(name='Members', value=invite.approximate_member_count)
        embed.add_field(name='Online', value=invite.approximate_presence_count)

        if invite.guild.features:
            embed.add_field(name='Special features', value='`'+'`\n`'.join(invite.guild.features)+'`', inline=False)

        try:
            embed.add_field(name='Invite created by', value=f"{invite.inviter.name}#{invite.inviter.discriminator} ({invite.inviter.mention})")
        except:
            pass

        if invite.guild.banner:
            embed.set_image(url=invite.guild.banner_url)
        elif invite.guild.splash:
            embed.set_image(url=invite.guild.splash_url)

        embed.set_thumbnail(url=invite.guild.icon_url)

        embed.set_footer(text=f"Server ID {invite.guild.id}")
        await ctx.reply(embed=embed)

def setup(bot):
    bot.add_cog(Guild(bot))