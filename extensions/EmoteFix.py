import discord
from discord.ext import commands
import re


class EmoteFix:
    """EmoteFix"""

    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        replaced = []
        match = re.findall("(?!<):.+?:(?!\\d+?>)", message.content)
        if match:
            shouldSend = False
            newmsg = message.content
            for emote in match:
                if not emote in replaced:
                    em = emote.replace(":", "")
                    for e in message.guild.emojis:
                        if e.name.lower() == em.lower():
                            if not e.animated:
                                continue
                            fullemote = "<a:" + str(em) + ":" + str(e.id) + ">"
                            newmsg = newmsg.replace(emote, fullemote)
                            replaced.append(emote)
                            shouldSend = True
            if shouldSend:
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
