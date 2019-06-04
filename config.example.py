from discord.ext import commands
token = "[TOKEN]"
description = "Lynn 3.0_DEV"

def get_prefix(bot, message):
    prefixes = ['%', 'lynn ']

    if not message.guild:
        return '%'

    return commands.when_mentioned_or(*prefixes)(bot, message)

api_keys = {
    "tracker":          "[KEY]",
    "steam":            "[KEY]",
    "openweathermap":   "[KEY]",
    "omdb":             "[KEY]"
}

steamIDs = {
        # Discord ID        :  Steam ID
        "123456789123456789": "123456789123456789",
}