from datetime import datetime
import discord
from discord.ext import commands

import bot.auction
import bot.verification
from bot.config import TOKEN


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

        await self.add_cog(bot.auction.Auction(self))
        await self.add_cog(bot.verification.Verification(self))


WOSPBot()
