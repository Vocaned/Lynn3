import discord
from discord.ext import commands
import re


class EmoteFix(commands.Cog):
    """EmoteFix"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        replaced = []
        shouldSend = False
        match = re.findall("(?=(:.+?:))", message.content)
        newmsg = message.content
        if match:
            for emote in match:
                if not emote in replaced:
                    em = emote.replace(":", "")
                    for e in message.guild.emojis:
                        if e.name.lower() == em.lower():
                            prefix = ""
                            if not e.animated:
                                continue
                            fullemote = "<a" + prefix + ":" + str(em) + ":" + str(e.id) + ">"
                            newmsg = newmsg.replace(emote, fullemote)
                            replaced.append(emote)
                            shouldSend = True

        match = re.findall("\\[.+]\\(<?https?://.+\\..+\\)", message.content)
        if match or shouldSend:
            hook = None
            for h in await message.channel.webhooks():
                if h.name == "EmoteFix":
                    hook = h
            if hook == None:
                hook = await message.channel.create_webhook(name="EmoteFix")
            await hook.send(content=newmsg, username=message.author.display_name, avatar_url=message.author.avatar_url)
            await message.delete()

def setup(bot):
    bot.add_cog(EmoteFix(bot))
