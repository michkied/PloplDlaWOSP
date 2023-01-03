from abc import ABC
from datetime import datetime
import discord
from discord.ext import commands
from logzero import logfile

from bot.auction import Auction
from bot.verification import Verification
from bot.config import TOKEN

# 0 - verification mode
# 1 - auction mode
mode = 1


class WOSPBot(commands.Bot, ABC):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or('?'),
            intents=discord.Intents.all(),
            auto_sync_commands=bool(mode)
        )

        self.remove_command('help')
        if mode:
            logfile("auction.log", encoding='UTF-8')
            self.add_cog(Auction(self))
            print('RUNNING IN AUCTION MODE')
        else:
            logfile("verification.log", encoding='UTF-8')
            self.add_cog(Verification(self))
            print('RUNNING IN VERIFICATION MODE')

        self.run(TOKEN)

    async def on_ready(self):
        date = datetime.now()
        print(f'We have logged in as {self.user}')
        print(self.user.display_name)
        print(self.user.id)
        print(date.strftime('%d.%m.%Y  %H:%M'))
        print('by Michał Kiedrzyński\n\n')


WOSPBot()
