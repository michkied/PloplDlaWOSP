# PloplDlaWOSP
#
# Made with Python 3.9 & ❤love❤ by Michał Kiedrzyński (michkied#6677)
# 2021 - 2022
#
# Gramy do końca świata i jeden dzień dzień dłużej!

import discord
from discord.ext import commands
from datetime import datetime

import auction
import verification

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='?', intents=intents)
bot.remove_command('help')


@bot.event
async def on_ready():
    date = datetime.now()
    print('Logged in as:')
    print(bot.user.name)
    print(bot.user.id)
    print(date.strftime('%d.%m.%Y  %H:%M'))
    print('by Michał Kiedrzyński')
    print('------')


if __name__ == '__main__':
    bot.add_cog(auction.Auction(bot))
    bot.add_cog(verification.Verification(bot))

    bot.run('TOKEN', reconnect=True)
