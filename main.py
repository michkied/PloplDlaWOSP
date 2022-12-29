from datetime import datetime
import discord
from discord.ext import commands
from logzero import logfile

import bot.auction
import bot.verification
from bot.config import TOKEN

# 0 - auction mode
# 1 - verification mode
mode = 0


class WOSPBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or('?'),
            intents=discord.Intents.all()
        )

        self.remove_command('help')
        self.run(TOKEN)

    async def on_ready(self):
        date = datetime.now()
        print(f'We have logged in as {self.user}')
        print(self.user.display_name)
        print(self.user.id)
        print(date.strftime('%d.%m.%Y  %H:%M'))
        print('by Michał Kiedrzyński\n\n')
        print("REMEMBER TO SEND A NEW POST MESSAGE")

        if mode:
            logfile("verification.log", encoding='UTF-8')
            await self.add_cog(bot.verification.Verification(self))
        else:
            logfile("auction.log", encoding='UTF-8')
            await self.add_cog(bot.auction.Auction(self))


WOSPBot()
