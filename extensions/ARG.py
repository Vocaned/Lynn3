import discord
from discord.ext import commands
from datetime import datetime
import base64


"""Commands useful for solving ARGs!"""


class ARG:
    """ARG"""

    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx):
        return ctx.message.guild.id != 485076757733572608

    @commands.command(name='guess')
    async def guess(self, ctx, *, data):
        """Command that guesses the encoding or format of data.
        Useful for ARGs and other puzzles."""
        if not data:
            await ctx.send('Please enter something to decrypt/decypher!')
            return
        data = str(data)
        method = [
            "Base64",
            "Base85",
            "Base32",
            "Hex",
            "Binary",
            "Decimal",
            "Octal",
            "Braille"
        ]
        value = []
        alphabet = " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!\"#%&/()=?'@$[]\\:.,:;"
        braille = "⠀⠁⠃⠉⠙⠑⠋⠛⠓⠊⠚⠅⠇⠍⠝⠕⠏⠟⠗⠎⠞⠥⠧⠺⠭⠽⠵⠁⠃⠉⠙⠑⠋⠛⠓⠊⠚⠅⠇⠍⠝⠕⠏⠟⠗⠎⠞⠥⠧⠺⠭⠽⠵⠴⠂⠆⠒⠲⠢⠖⠶⠦⠔⠮⠐⠼⠩⠯⠌⠷⠾⠿⠹⠄⠈⠫⠪⠻⠳⠱⠨⠠⠱⠰"
        transbraille = str.maketrans(braille, alphabet)
        for m in method:
            try:
                if m == "Base64":
                    value.append(base64.b64decode(data).decode("utf-8"))
                elif m == "Base85":
                    value.append(base64.a85decode(data).decode("utf-8"))
                elif m == "Base32":
                    value.append(base64.b32decode(data).decode("utf-8"))
                elif m == "Hex":
                    value.append(bytes.fromhex(data).decode('utf-8'))
                elif m == "Binary":
                    n = int(data.replace(' ',''), 2)
                    value.append(n.to_bytes((n.bit_length() + 7) // 8, 'big').decode())
                elif m == "Decimal":
                    o = []
                    for c in data.split():
                        o.append(chr(int(c)))
                    value.append(''.join(o))
                elif m == "Octal":
                    o = []
                    for c in data.split():
                        o.append(chr(int(c, 8)))
                    value.append(''.join(o))
                elif m == "Braille":
                    value.append(data.translate(transbraille))
                else:
                    value.append("[ERROR]")
            except:
                value.append('Invalid data')
        message = await ctx.send('\N{HOURGLASS}')
        embed = discord.Embed(title='ARG Guess', colour=0x551a8b)
        for i in range(len(method)):
            embed.add_field(name=method[i], value=value[i])
        embed.timestamp = datetime.utcnow()
        await message.edit(embed=embed, content="")

# The setup fucntion below is neccesarry. Remember we give bot.add_cog() the name of the class in this case SimpleCog.
# When we load the cog, we use the name of the file.
def setup(bot):
    bot.add_cog(ARG(bot))