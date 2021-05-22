from discord.ext import commands
from BotUtils import REST, getAPIKey, escapeURL
from datetime import datetime
import discord
import typing
import database

class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='weather')
    async def WeatherAPI(self, ctx, *, city: typing.Optional[typing.Union[discord.Member, str]]):
        """Gets information about the weather"""
        hidden = False
        if not city:
            city = await database.getValue('users', ctx.author.id, 'location')
            if not city:
                raise commands.UserInputError(message='No location set for user')
        elif type(city) is discord.Member:
            city = await database.getValue('users', city.id, 'location')
            if not city:
                raise commands.UserInputError(message='No location set for user')

        if city.endswith('(hidden)'):
            city = city.replace('(hidden)', '').strip()
            hidden = True

        geocoding = await REST('https://nominatim.openstreetmap.org/search?format=json&limit=1&accept-language=en&q='+escapeURL(city))
        data = await REST(f"https://api.darksky.net/forecast/{getAPIKey('darksky')}/{geocoding[0]['lat']},{geocoding[0]['lon']}?exclude=minutely,hourly,daily,flags&units=si")

        try:
            if data['alerts']:
                col = 0xff0000
            else:
                col = 0xffb347
        except:
            col = 0xffb347

        if hidden:
            embed = discord.Embed(title='(location hidden)', color=col)
        else:
            embed = discord.Embed(title=geocoding[0]['display_name'], color=col)
        embed.set_thumbnail(url=f"https://darksky.net/images/weather-icons/{data['currently']['icon']}.png")
        try:
            if not hidden:
                alerts = []
                for alert in data['alerts']:
                    if len(alerts) > 3:
                        continue
                    if alert['title'] not in alerts:
                        embed.add_field(name=alert['title'], value=alert['description'][:1024])
                        alerts.append(alert['title'])
        except:
            pass
        embed.add_field(name=data['currently']['summary'], value=str(round(data['currently']['temperature'], 2)) + '°C (' + str(round(data['currently']['temperature'] * (9/5) + 32, 2)) + '°F)\n' \
            + 'Feels Like: ' + str(round(data['currently']['apparentTemperature'], 2)) + '°C (' + str(round(data['currently']['apparentTemperature'] * (9/5) + 32, 2)) + '°F)\n' \
            + 'Humidity: ' + str(round(data['currently']['humidity'] * 100, 2)) + '%\n' \
            + 'Clouds: ' + str(round(data['currently']['cloudCover'] * 100, 2)) + '%\n' \
            + 'Wind: ' + str(data['currently']['windSpeed']) + ' m/s (' + str(round(int(data['currently']['windSpeed']) * 2.2369362920544, 2)) + ' mph)', inline=False)
        embed.set_footer(text='Powered by Dark Sky and OpenStreetMap')
        embed.timestamp = datetime.utcfromtimestamp(data['currently']['time'])
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Weather(bot))