from discord.ext import commands
import logging
from datetime import datetime
token = "[TOKEN]"
description = "Lynn 3.0_DEV"
gitURI = "git@github.com:Fam0r/Lynn3.git"
cogDir = "extensions"

logging.basicConfig(format='%(asctime)s | [%(levelname)s] (%(filename)s) - %(message)s',
                    level=logging.INFO,
                    handlers=[
                        logging.FileHandler("logs/"+datetime.now().strftime('%Y-%m-%d')+".log"),
                        logging.StreamHandler()
                    ])

def get_prefix(bot, message):
    prefixes = ['%', 'lynn ']
    if not message.guild:
        return '%'
    return commands.when_mentioned_or(*prefixes)(bot, message)

apiKeys = {
    "tracker":          "[KEY]",
    "steam":            "[KEY]",
    "darksky":          "[KEY]",
    "omdb":             "[KEY]",
    "mapbox":           "[KEY]",
    "twitterConsKey":   "[KEY]",
    "twitterConsSecret":"[KEY]",
    "twitterAccToken":  "[KEY]",
    "twitterAccSecret": "[KEY]",
    "osu":              "[KEY]",
    "twitchID":         "[KEY]",
    "twitchSecret":     "[KEY]"
}

statusPages = [
    ("discord", "https://status.discordapp.com"),
    ("twitter", "https://api.twitterstat.us"),
    ("reddit", "https://reddit.statuspage.io"),
    ("cloudflare", "https://www.cloudflarestatus.com"),
    ("dropbox", "https://status.dropbox.com"),
    ("github", "https://www.githubstatus.com"),
    ("medium", "https://medium.statuspage.io"),
    ("epicgames", "https://status.epicgames.com"),
    ("glitch", "https://status.glitch.com")
]