from datetime import datetime
import discord
from discord.ext import commands

import auction
import verification
from config import TOKEN

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='?', intents=intents)
bot.remove_command('help')


@bot.event
async def on_ready():
    date = datetime.now()
    print(f'We have logged in as {bot.user}')
    print(bot.user.display_name)
    print(bot.user.id)
    print(date.strftime('%d.%m.%Y  %H:%M'))
    print('by Michał Kiedrzyński\n\n')
    print("REMEMBER TO SEND A NEW POST MESSAGE")

    await bot.add_cog(auction.Auction(bot))
    await bot.add_cog(verification.Verification(bot))


if __name__ == "__main__":
    bot.run(TOKEN)
