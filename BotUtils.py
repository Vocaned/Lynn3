import discord
from datetime import datetime
from discord.ext import commands
import requests
from PIL import Image, ImageOps

async def embedMsg(channel, hex, title="", description=""):
    embed = discord.Embed(title=str(title), colour=hex)
    embed.description = str(description)
    embed.timestamp = datetime.utcnow()
    return await channel.send(embed=embed, content='')

async def skinRenderer2D(url, filename):
    """Renders a skin in 2D and returns path to the saved file"""

    img = Image.open(requests.get(url, stream=True).raw)
    p = int(img.width / 64)
    w = int(p*16)
    l = img.width == img.height

    img2 = Image.new("RGBA", (w, w*2), color=000000)

    headSize = (p*8, p*8, p*16, p*16)
    head2Size = (p*40, p*8, p*48, p*16)
    head = img.crop(headSize).convert("RGBA")
    head2 = img.crop(head2Size).convert("RGBA")
    head = Image.alpha_composite(head, head2)
    # p*(w/2-p*8/2)
    img2.paste(head, (p*4, 0))

    bodySize = (p*20, p*20, p*28, p*32)
    body = img.crop(bodySize).convert("RGBA")
    if l:
        body2Size = (p*20, p*36, p*28, p*48)
        body2 = img.crop(body2Size).convert("RGBA")
        body = Image.alpha_composite(body, body2)
    img2.paste(body, (p*4, p*8))

    if not l:
        # 64x32 format
        armSize = (p*44, p*20, p*48, p*32)
        arm = img.crop(armSize)
        img2.paste(arm, (0, p*8))
        arm = ImageOps.mirror(arm)
        img2.paste(arm, (img2.width-p*4, p*8))
        
        legSize = (p*4, p*20, p*8, p*32)
        leg = img.crop(legSize)
        img2.paste(leg, (p*4, p*20))
        leg = ImageOps.mirror(leg)
        img2.paste(leg, (img2.width-p*8, p*20))
    else:
        # 64x64 format
        rArmSize = (p*44, p*20, p*48, p*32)
        rArm2Size = (p*44, p*36, p*48, p*48)
        rArm = img.crop(rArmSize).convert("RGBA")
        rArm2 = img.crop(rArm2Size).convert("RGBA")
        rArm = Image.alpha_composite(rArm, rArm2)
        img2.paste(rArm, (0, p*8))

        lArmSize = (p*36, p*52, p*40, p*64)
        lArm2Size = (p*52, p*52, p*56, p*64)
        lArm = img.crop(lArmSize).convert("RGBA")
        lArm2 = img.crop(lArm2Size).convert("RGBA")
        lArm = Image.alpha_composite(lArm, lArm2)
        img2.paste(lArm, (img2.width-p*4, p*8))
        
        rLegSize = (p*4, p*20, p*8, p*32)
        rLeg2Size = (p*4, p*36, p*8, p*48)
        rLeg = img.crop(rLegSize).convert("RGBA")
        rLeg2 = img.crop(rLeg2Size).convert("RGBA")
        rLeg = Image.alpha_composite(rLeg, rLeg2)
        img2.paste(rLeg, (p*4, p*20))

        lLegSize = (p*20, p*52, p*24, p*64)
        lLeg2Size = (p*4, p*52, p*8, p*64)
        lLeg = img.crop(lLegSize).convert("RGBA")
        lLeg2 = img.crop(lLeg2Size).convert("RGBA")
        lLeg = Image.alpha_composite(lLeg, lLeg2)
        img2.paste(lLeg, (img2.width-p*8, p*20))

    if img2.width < 256:
        img2 = img2.resize((img2.width * 16, img2.height * 16), resample=Image.NEAREST)
    img2.save("skins/2d/" + str(filename) + ".png")
    return "skins/2d/" + str(filename) + ".png"