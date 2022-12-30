from abc import ABC
from datetime import datetime
import discord
from discord.ext import commands
from logzero import logfile

from bot.auction import Auction
from bot.verification import Verification
from bot.config import TOKEN

# 0 - auction mode
# 1 - verification mode
mode = 1


class WOSPBot(commands.Bot, ABC):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or('?'),
            intents=discord.Intents.all()
        )

        self.remove_command('help')
        if mode:
            logfile("verification.log", encoding='UTF-8')
            self.add_cog(Verification(self))
            print('RUNNING IN VERIFICATION MODE')
        else:
            logfile("auction.log", encoding='UTF-8')
            self.add_cog(Auction(self))
            print('RUNNING IN AUCTION MODE')

        self.run(TOKEN)

    async def on_ready(self):
        date = datetime.now()
        print(f'We have logged in as {self.user}')
        print(self.user.display_name)
        print(self.user.id)
        print(date.strftime('%d.%m.%Y  %H:%M'))
        print('by Michał Kiedrzyński\n\n')


WOSPBot()
