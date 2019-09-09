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
        newmsg = message.content
        match = re.findall(".*:\\S+?:.*", message.content)
        if match:
            for emote in match:
                if re.match("<a:\\S+:\\d{18}>", emote) is None and not emote in replaced:
                    em = emote.replace(":", "")
                    for e in message.guild.emojis:
                        if e.name.lower() == em.lower():
                            prefix = ""
                            # TODO: Don't do anything if message author has nitro
                            if not e.animated:
                                # TODO: Blob emotes
                                continue
                            else:
                                prefix = "a"
                            fullemote = "<" + prefix + ":" + str(em) + ":" + str(e.id) + ">"
                            newmsg = newmsg.replace(emote, fullemote)
                            replaced.append(emote)
                            shouldSend = True

        match = re.findall("\\[.+]\\(<?https?://.+\\..+\\)", message.content)
        if match or shouldSend:
            hook = [h for h in await message.channel.webhooks() if h.name == "EmoteFix"][0]
            if not hook:
                hook = await message.channel.create_webhook(name="EmoteFix")
            await hook.send(content=debug, username=message.author.display_name, avatar_url=message.author.avatar_url)
            await message.delete()

def setup(bot):
    bot.add_cog(EmoteFix(bot))
