import requests
import random
from PIL import Image
from collections import defaultdict,Counter
from io import BytesIO
from bs4 import BeautifulSoup
import os
import cv2
import numpy as np
import textwrap
import shutil
import cairosvg
import sqlite3
import re
import itertools
import math
import sys

TOOBIG		= -1	
TOOSMALL	= -2
NOTNEW		= -3
EMPTY		= -1

class NameJoiner():


	def __init__(self, str1, str2):
		words = [str1, str2]
		random.shuffle(words)
		self.fullStartName = words[0]
		self.fullEndName   = words[1]
		self.initVariables()
	
	def initVariables(self):
		self.lower_limit = min(len(self.fullStartName), len(self.fullEndName))
		self.upper_limit = max(len(self.fullStartName), len(self.fullEndName)) + self.lower_limit -1	
		self.firstPositions  = self.getKeyVocalsPositions(self.fullStartName)
		self.secondPositions = self.getKeyVocalsPositions(self.fullEndName)

	def join(self):
		
		res = self.tryToJoin()
		if res == -1:
			self.fullStartName, self.fullEndName = self.fullEndName, self.fullStartName
			self.initVariables()
			res = self.tryToJoin()
		
		if res == -1:
			self.initVariables()
			return self.fullStartName+self.fullEndName[self.secondPositions[-1]+1:]
			print("DEP", self.fullEndName, self.fullStartName)
			sys.exit(0)
			return "DEP"
			
		
		return res

	def tryToJoin(self):
		
		firstSplitPlace = self.chooseRandomFirstSplit()
		secondSplitPlace = NOTNEW
		while secondSplitPlace < 0:	
			secondSplitPlace = self.chooseRandomSecondSplit(firstSplitPlace)
			
			if(secondSplitPlace < 0):
				self.handleErrorWithFirstPlace(secondSplitPlace, firstSplitPlace)
				firstSplitPlace = self.chooseRandomFirstSplit()
				if firstSplitPlace == EMPTY: return EMPTY
			
			else:	
				namex = self.fullStartName[:firstSplitPlace] + self.fullEndName[secondSplitPlace:]
				if self.fullEndName == namex or self.fullStartName == namex:
					self.secondPositions = [i for i in self.secondPositions if i != secondSplitPlace-1]
					if(len(self.secondPositions) == 0):
						self.secondPositions = self.getKeyVocalsPositions(self.fullEndName)
						self.firstPositions = self.erasePlaceEq(firstSplitPlace)
						firstSplitPlace = self.chooseRandomFirstSplit()
						if firstSplitPlace == EMPTY: return EMPTY
							
					secondSplitPlace = NOTNEW

		return self.fullStartName[:firstSplitPlace] + self.fullEndName[secondSplitPlace:]

	def handleErrorWithFirstPlace(self, error, firstSplitPlace):
		if(error == TOOBIG): # Need smaller first part
			self.firstPositions = self.erasePlacesGreaterEq(firstSplitPlace)

		elif(error == TOOSMALL): # Need greater first part
			self.firstPositions = self.erasePlacesLowerEq(firstSplitPlace)

	def erasePlaceEq(self, position):
		p = position - 1
		res = [i for i in self.firstPositions if i != p]
		
		return res

	def erasePlacesLowerEq(self, position):
		p = position - 1
		res = [i for i in self.firstPositions if i > p]
		
		return res

	def erasePlacesGreaterEq(self, position):
		p = position - 1
		res = [i for i in self.firstPositions if i < p]
		
		return res

	def chooseRandomFirstSplit(self):

		if len(self.firstPositions) == 0:
			print( f"{self.fullStartName} has been omitted while trying to join with {self.fullEndName}" )
			return -1		
		pos = random.choice(self.firstPositions) + 1

		return pos

	def getKeyVocalsPositions(self, s):
		regex_iter = re.finditer(r'[aeiouy][^aeiou]', s.lower())
		positions = [ i.start() for i in regex_iter]	
		return positions
	
	def chooseRandomSecondSplit(self, firstSplitPlace):
		
		minimumCharactersLeft = self.lower_limit - firstSplitPlace
		maximumCharactersLeft = self.upper_limit - firstSplitPlace

		minimumIndex = len(self.fullEndName) - maximumCharactersLeft
		maximumIndex = len(self.fullEndName) - minimumCharactersLeft

		filtered_big_positions = [i for i in self.secondPositions if i <= maximumIndex]
		#print("big", *[self.fullEndName[i:] for i in filtered_big_positions])
		if len(filtered_big_positions) == 0: return -2
		filtered_positions = [i for i in self.secondPositions if i+1 >= minimumIndex and i+1 <= maximumIndex]
		#print("all", *[self.fullEndName[i:] for i in filtered_positions])
		if len(filtered_positions) == 0: return -1

		return random.choice(filtered_positions) + 1 

class CountryMixer():
    def rgb2hex(self,color):
        r,g,b = color
        code = "#{:02x}{:02x}{:02x}".format(r,g,b)
        return code

    def smallerHex(self, bigHex):
        smaller = "#"
        for i in [1,3,5]:
            smaller += bigHex[i]
        return smaller

    def getPais(self, code):
        pais = None
        if code.lower() == 'russia':
            code = 'RU'
        for n in self.info_banderas:
            if n['name'].lower() == code.lower() or n['alpha3Code'].lower() == code.lower() or n['alpha2Code'].lower() == code.lower():
                pais = n
        if not pais:
            raise Exception("No country found: " + code)
        return pais

    def getVecinos(self):
        tenemos = False
        while not tenemos:
            pais1 = random.choice(self.info_banderas)

            bandera1 = pais1['alpha3Code']
            if len(pais1['borders']) > 0:
                frontera =random.choice(pais1['borders'])
                for n in self.info_banderas:
                    if n['alpha3Code'] == frontera:
                        pais2 = n


                if pais1 and pais2:
                    tenemos = True


        self.pais1 = pais1
        self.pais2 = pais2
        self.paises = (self.pais1, self.pais2)
        for pais in self.paises:
            self.downloadPNGFlag(pais["alpha3Code"])

    def getImagen(self, datos, num):
        tenemos = False
        while not tenemos:
            pais1 = random.choice(datos)
            tenemos = True


        return pais1

    def getEmoji(self, code):
        return (code)

    def updateDbWithBase(self,template):
        conn = sqlite3.connect('paises.db')
        c = conn.cursor()
        pais1,pais2 = sorted([self.pais1['alpha2Code'],self.pais2['alpha2Code']])

        c.execute('update paises set base=(?) where pais1=(?) and pais2=(?) and base is null', (template,pais1,pais2))
        conn.commit()

    def insertPaises(self):
        conn = sqlite3.connect('paises.db')
        c = conn.cursor()
        pais1,pais2 = sorted([self.pais1['alpha2Code'],self.pais2['alpha2Code']])
        c.execute('insert into paises values (?,?,?)', (pais1,pais2,None))
        conn.commit()

    def isAlreadyDone(self, template, colors):
        conn = sqlite3.connect('paises.db')
        c = conn.cursor()
        pais1,pais2 = sorted([template, colors])
        c.execute("select * from paises where pais1=? and pais2=? and base=?", (pais1, pais2, template))
        rows = c.fetchall()

        return len(rows) != 0

    def checkMashupValid(self):
        conn = sqlite3.connect('paises.db')
        c = conn.cursor()
        pais1,pais2 = sorted([self.pais1['alpha2Code'],self.pais2['alpha2Code']])
        if pais1 == "NU" or pais2 == "NU":
            return False
        c.execute('select * from paises where pais1=? and pais2=?', (pais1,pais2))
        rows = c.fetchall()
        if (len(rows)==1 and rows[0][2]):
            co = Counter(rows[0])
            self.template3Code =co.most_common()[-1][0]
            if self.template3Code == self.pais1['alpha2Code']:
                self.template3Code= self.pais1['alpha3Code']
            else:
                self.template3Code = self.pais2['alpha3Code']
            return True
        elif len(rows)<1:
            self.template3Code = None

            return True
        else:
            self.template3Code = None

            return False

    def getFullFlagsInfoJSON(self):
        info = requests.get("https://restcountries.eu/rest/v2/all")
        if info.status_code != 200:
            raise RuntimeError("Can't get full flags info")

        return info.json()

    def chooseRandomFlag(self, alreadyChoosen=None):

        while True:
            flag = random.choice(self.info_banderas)
            if flag['alpha3Code'] != alreadyChoosen:
                return flag

    def downloadPNGFlag(self, alpha3Code):
        #r = open(f"paises/{alpha3Code.lower()}.svg","r")
        r = requests.get(f"https://restcountries.eu/data/{alpha3Code.lower()}.svg")
        cairosvg.svg2png(bytestring=r.text,write_to=f'{alpha3Code.lower()}.png')

    def randomlyDownloadFlags(self):

        self.pais1 = self.chooseRandomFlag()
        self.pais2 = self.chooseRandomFlag()
        #self.pais2 = self.pais1
        self.paises = (self.pais1, self.pais2)

        for pais in self.paises:
            self.downloadPNGFlag(pais["alpha3Code"])

    def getFlagsEmojis(self):
        emojis = []

        for pais in self.paises:
            codigo = pais['alpha2Code']
            emoji = (chr(ord(codigo[0]) + 127397) + chr(ord(codigo[1]) + 127397))
            emojis.append(emoji)

        return emojis

    def getFlagsSortedColors(self):


        flagsSortedColors = []

        for pais in self.paises:
            img = Image.open(f'{pais["alpha3Code"].lower()}.png')
            width, height = img.size
            limite = ((width*height)*.01)
            colors = img.convert('RGBA').getcolors(
                img.size[0]*img.size[1])  # this converts the mode to RGB
            colors = sorted(colors, key=lambda x: x[0], reverse=True)
            colors = [ c for c in colors if c[1][3] is not 0]
            
            colorb1 = [self.rgb2hex(color[1][:3]) for color in colors[:5]  if color[0] > limite ]

            combis = itertools.combinations(colorb1,2)
            colores = []
            for pareja in combis:
                r1,g1,b1 =  tuple(int(pareja[0].replace("#","")[i:i+2], 16) for i in (0, 2, 4))
                r2,g2,b2 =  tuple(int(pareja[1].replace("#","")[i:i+2], 16) for i in (0, 2, 4))
                dif = math.sqrt(math.pow(r1 - r2,2 ) + math.pow(g1  - g2 , 2) + math.pow(b1  - b2 , 2))
                if dif < 50 and pareja[1] in colorb1:
                    colorb1.remove(pareja[1])
            flagsSortedColors.append(colorb1)
        return flagsSortedColors
    def selectTemplateAndColors(self, nameColorList):

        FIRSTCOUNTRY = NAME   = 0
        LASTCOUNTRY  = COLORS = 1

        template = nameColorList[FIRSTCOUNTRY][NAME]
        colors = nameColorList[LASTCOUNTRY][NAME]

        if len(nameColorList[FIRSTCOUNTRY][COLORS]) > len(nameColorList[LASTCOUNTRY][COLORS]):
            template, colors = colors, template

        elif len(nameColorList[FIRSTCOUNTRY][COLORS]) == len(nameColorList[LASTCOUNTRY][COLORS]):
            if (random.randint(0,2) == 0):
                template, colors = colors, template

            if(self.isAlreadyDone(self.paises[template]["alpha2Code"], self.paises[colors]["alpha2Code"])):
                template, colors = colors, template
                
            if self.pais1 is not self.pais2:
                self.updateDbWithBase(self.paises[template]["alpha2Code"])

        if not self.template3Code:
            self.template3Code = self.paises[template]['alpha3Code']
        templateSVG = requests.get(f"https://restcountries.eu/data/{self.template3Code.lower()}.svg")
        #templateSVG = open(f"paises/{self.template3Code.lower()}.svg","r").read()
        
        for i in nameColorList:

            if i[NAME] == colors :
                newColors = i[COLORS]
            else:
                oldColors = i[COLORS]

        if self.pais1 == self.pais2 :
            newColors = reversed(newColors)

        colorsDict = dict(zip(newColors, oldColors))

        return templateSVG.text, colorsDict



    def clean(self,texto):
        archivo = open("colores.dat","r")
        codigos = archivo.readlines()
        codigos = [c.split(",") for c in codigos]
        clean = {}
        for c in codigos:
            c = c[0].split()
            clean[c[0].lower()] = c[1].replace("\n","")

        
        data2 = texto
        for key,value in clean.items():
            tag = f'fill="{key}"'

            if tag in data2:
                nuevo_val = f'fill="{value}"'
                data2 = data2.replace(tag,nuevo_val)
            tag = f'fill:{key}'

            if tag in data2:
                nuevo_val = f'fill:{value}'
                data2 = data2.replace(tag,nuevo_val)
        

        if data2 is not texto:
            texto = data2
        
        root = BeautifulSoup(texto,"lxml")
        svg = root.find("svg")

        paths = svg.findAll('rect', recursive=False)
        modi = False
        for t in paths:
            fill = t.get("fill")

            if fill == None  and t.get("style") == None and t.get("stroke") == None:
                t['fill'] ="#000000"
                modi = True


        paths = svg.findAll('path', recursive=False)


        for t in paths:
            fill = t.get("fill")

            if fill == None and t.get("style") == None and t.get("stroke") == None:
                t['fill'] ="#000000"
                modi = True

        if (modi):
            datos = str(svg).replace("<html><body>","\n").replace("</body></html>","")
            texto = datos



        return texto

    def changeColors(self, cambios):
        self.svgText = self.clean(self.svgText)
        for new, old in cambios.items():
            self.svgText = self.svgText.replace(old, new.replace('#','ç'))
            self.svgText = self.svgText.replace(old.upper(), new.replace('#','ç'))

        for new, old in cambios.items():
            self.svgText = self.svgText.replace(self.smallerHex(old), new.replace('#','ç'))
            self.svgText = self.svgText.replace(self.smallerHex(old).upper(), new.replace('#','ç'))

        self.svgText = self.svgText.replace('ç', '#')

    def calculateNames(self):
        name1 = self.pais1['name']
        name2 = self.pais2['name']


        if "(" in name1:
            p_temp = name1.split("(")
            name1 = p_temp[1].replace(")","") +" " + p_temp[0]

        if "(" in name2:
            p_temp = name2.split("(")
            name2 = p_temp[1].replace(")","") +" " + p_temp[0]

        if "," in name1:
            p_temp = name1.split(", ")
            name1 = p_temp[1] +" " + p_temp[0]

        if "," in name2:
            p_temp = name2.split(", ")
            name2 = p_temp[1] +" " + p_temp[0]

        self.pais1['name'] = name1
        self.pais2['name'] = name2



        if len(name2.split())>1 :
            name = (" ".join(name2.split()[:-1])+ " " + name1.split()[-1] )
        elif len(name1.split())>1 :
            name= (" ".join(name1.split()[:-1])+ " " + name2.split()[-1] )
        else:
            #name = self.portnameteau([self.pais1['name'],self.pais2['name']])
            name = NameJoiner(self.pais1['name'],self.pais2['name']).join()
        if (name1 == name2):
            name = name1 + " 2"
        return name


    def saveToPNG(self):
        image = Image.open(f'{self.template3Code.lower()}.png')
        width, height = image.size
        subido = False
        bigger = max(width, height)
        if bigger > 4096:bigger = 4096
        while not subido:
            cairosvg.svg2png(bytestring=self.svgText,write_to='output.png', scale=int(4096/bigger))
            tamanho = os.stat("output.png").st_size/1024
            limit_kb = 3072
            if tamanho<limit_kb: 
                subido =True
            else: 
                bigger = bigger * 1.25


    def mixFlags(self):
        colorb1, colorb2 = self.getFlagsSortedColors()

        template, colors = self.selectTemplateAndColors( [(0, colorb1), (1, colorb2)] )
        self.svgText = template
        self.changeColors(colors)
        self.saveToPNG()
        if self.template3Code == self.pais2['alpha3Code']:
            return colorb1[0]
        return colorb2[0]

    def removePNGs(self):
        i = 1
        for p in self.paises:
            try:
                ruta = f'{p["alpha3Code"].lower()}.png'
                nruta = f'bandera{i}.png'
                i = i + 1
                shutil.move(ruta,nruta) 
            except:
                print("no fue posible elimiar", ruta)

    def manuallyDownloadFlags(self, alpha3CodeFlag1=None, alpha3CodeFlag2=None):
        if not alpha3CodeFlag1:
            self.pais1 = self.chooseRandomFlag()
        else:
            self.pais1 = self.getPais(alpha3CodeFlag1)

        if not alpha3CodeFlag2:
            self.pais2 = self.chooseRandomFlag()
        else:
            self.pais2 = self.getPais(alpha3CodeFlag2)

        self.paises = (self.pais1, self.pais2)

        self.downloadPNGFlag(self.pais1["alpha3Code"])
        self.downloadPNGFlag(self.pais2["alpha3Code"])



    def main(self, country1=None, country2=None):
        if (country1 and country1.lower() == "none"): country1 = None
        if (country2 and country2.lower() == "none"): country2 = None

        self.info_banderas = self.getFullFlagsInfoJSON()

        self.manuallyDownloadFlags(alpha3CodeFlag1=country1, alpha3CodeFlag2=country2)

        self.checkMashupValid()

        self.insertPaises()
        color = self.mixFlags()
        name = self.calculateNames()

        self.removePNGs()
        return [self.pais1["name"], self.pais2["name"]], self.getFlagsEmojis(), name, color

import discord
import random
from discord.ext import commands

class FlagMashup(commands.Cog):
    '''FlagMashup'''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='flagmashup', aliases=['mashup', 'flag', 'fm'])
    async def flagmashup(self, ctx, country1=None, country2=None):
        '''Combines 2 country flags together. Use the country's full name.
        Use "none" for a random flag'''
        c = CountryMixer()
        data = c.main(country1=country1, country2=country2)
        print(data)
        color = data[3].strip('#')
        if (color == 'ffffff'): color = 'fefefe'
        if (color == '000000'): color = '010101'

        embed = discord.Embed(title=f'{data[0][0]} {data[1][0]} + {data[0][1]} {data[1][1]} = {data[2]}', color=int(color, 16))
        flag = discord.File('output.png')
        embed.set_image(url=f'attachment://output.png')
        await ctx.reply(file=flag, embed=embed)

def setup(bot):
    bot.add_cog(FlagMashup(bot))

if __name__ == "__main__":
    c = CountryMixer()
    print(c.main(country1=input('first: '), country2=input('second: ')))