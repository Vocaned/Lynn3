import os
import discord
from discord.ext import commands
import platform
import asyncio
import random
import time
import subprocess
import pyscreenshot
import io
from pynput.keyboard import Key, Controller

pathtorom = os.path.join(os.getcwd(), "pokemonyellow.gb")
msg = None
ch = None
UpdateLimit = 2
CurrentUpdate = 0
keyboard = Controller()

movtime = 0.25
emotes = {"LeftArrow": "\u2B05", "DownArrow": "\u2B07", "UpArrow": "\u2B06", "RightArrow": "\u27A1", "AButton": "\U0001F170", "BButton": "\U0001F171", "Start": "\u25B6", "Select": "\U0001F502"}


"""Gameboy Emulator"""


class GB(commands.Cog):
    """GB"""

    def __init__(self, bot):
        self.bot = bot
        asyncio.ensure_future(self.UpdateFrame())

    def IsValidReaction(self, react):
        global emotes
        for emote in emotes:
            if (react == emotes[emote]):
                return True
        return False
    
    def GetWindowCoords(self):
        outs = str(subprocess.check_output(["wmctrl", "-lG"]))[2:-1].split("\\n")
        for f in outs:
            if (f.find("Gambatte SDL") != -1): #Found Window
                f2 = f.split(" ")
                f = []
                for elem in f2:
                    if (elem != ""):
                        f.append(elem)

                # Brut
                X1 = int(f[2]) - 2
                Y1 = int(f[3])
                X2 = X1 + int(f[4]) - 2
                Y2 = Y1 + int(f[5])
                return (X1, Y1, X2, Y2)
        return None
    
    async def SendImage(self, react=False):
        global msg
        global ch
        global emotes
        coords = self.GetWindowCoords()
        os.system("wmctrl -a 'Gambatte SDL'") # Focus Window
        im = pyscreenshot.grab(bbox=(coords[0], coords[1], coords[2], coords[3])) # X1,Y1,X2,Y2
        im.save("frame.jpg")
        msgold = msg
        msg = await ch.send(file=discord.File("frame.jpg"))
        if (msgold != None):
            await msgold.delete()
        if (react):
            await msg.add_reaction(emotes["AButton"])
            await msg.add_reaction(emotes["BButton"])
            await msg.add_reaction(emotes["LeftArrow"])
            await msg.add_reaction(emotes["DownArrow"])
            await msg.add_reaction(emotes["UpArrow"])
            await msg.add_reaction(emotes["RightArrow"])
            await msg.add_reaction(emotes["Start"])
            await msg.add_reaction(emotes["Select"])

    async def UpdateFrame(self):
        global msg
        global CurrentUpdate
        global UpdateLimit
        while True:
            if (ch != None):
                CurrentUpdate += 1
                if (CurrentUpdate < UpdateLimit):
                    asyncio.sleep(0.5)
                elif (CurrentUpdate == UpdateLimit):
                    print ("Updating Frame+Emojis...")
                    await self.SendImage(True) # React
                    print ("All good.")
                else:
                    await asyncio.sleep(0.5)
            else:
                await asyncio.sleep(0.5)

    async def SendKey(self, k, movkey=False):
        global keyboard
        global movtime
        keyboard.press(k)
        if (movkey == False):
            await asyncio.sleep(0.25)
        else:
            await asyncio.sleep(movtime)
    
        keyboard.release(k)


    @commands.command(aliases=['gb'])
    async def gameboy(self, ctx):
        """Generates a game of minesweeper."""
        global msg
        global ch
        global CurrentUpdate
        global movtime
        if (self.GetWindowCoords() == None): # No emulator running
            os.system("./gambatte_sdl " + pathtorom + " --scale 2 &")
            
        while (self.GetWindowCoords() == None): # Avoid any issues
            time.sleep(0.1)

        ch = ctx.channel
        msg = None
        CurrentUpdate = 0

    @commands.command()
    async def stopGB(self, ctx):
        global ch
        ch = None

    async def on_reaction_add(self, reaction, user):
        global msg
        global emotes
        global CurrentUpdate
        if (reaction.message.id == msg.id and reaction.count != 1): # We got a react
            reaction = str(reaction) # Simplify
            if (self.IsValidReaction(reaction)):
                print ("Input Received: " + reaction)
                os.system("wmctrl -a 'Gambatte SDL'") # Focus Window
    
                if (reaction == emotes["LeftArrow"]):
                    await self.SendKey(Key.left, True)
                elif (reaction == emotes["DownArrow"]):
                    await self.SendKey(Key.down, True)
                elif (reaction == emotes["UpArrow"]):
                    await self.SendKey(Key.up, True)
                elif (reaction == emotes["RightArrow"]):
                    await self.SendKey(Key.right, True)
                elif (reaction == emotes["AButton"]):
                    await self.SendKey("d")
                elif (reaction == emotes["BButton"]):
                    await self.SendKey("c")
                elif (reaction == emotes["Start"]):
                    await self.SendKey(Key.enter)
                elif (reaction == emotes["Select"]):
                    await self.SendKey(Key.shift_r)
    
                CurrentUpdate = 0



def setup(bot):
    bot.add_cog(GB(bot))
