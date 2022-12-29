import pathlib
from logzero import logger, logfile
from discord.ext import commands
from discord import app_commands
import json
from .config import *

path = str(pathlib.Path(__file__).parent.absolute())
logfile("auction.log")

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


def update(data):
    with open(path+r'\\data.json', 'w+', encoding='UTF-8') as f:
        f.write(json.dumps(data))
    with open(path+r'\\price.txt', 'w+', encoding='UTF-8') as f:
        f.write(str(data['price']) + 'zł')
    with open(path+r'\\sum.txt', 'w+', encoding='UTF-8') as f:
        f.write(str(data['sum']) + 'zł')


class Auction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open(path+'\\data.json', 'r+', encoding="UTF-8") as f:
            self.data = json.loads(f.read())

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.channel.id == auction_channel and msg.author.id != self.bot.user.id:
            is_moderator = auction_organizator_id in list(map(lambda x: x.id, msg.author.roles))

            try:
                new_price = int(msg.content.lower().replace('zł', '').replace('pln', '').replace('zl', '').replace('!', ''))
            except (ValueError, TypeError):
                if not is_moderator:
                    await msg.delete()
                    logger.warning(f"{msg.author.display_name} napisał {msg.content}")
                return

            if self.data['running']:
                if new_price - self.data['price'] > 9000:
                    await self.bot.get_channel(log_channel).send(f'{msg.author.mention} próbował/a podbić cenę '
                                                                 f'o {new_price - self.data["price"]}')
                    await msg.delete()
                    logger.warning(f"{msg.author.display_name} próbował podbić cenę o {new_price - self.data['price']}")
                    return

                if new_price < self.data['price'] + 2:
                    await msg.delete()
                    try:
                        await msg.author.send(':x: **Podana przez ciebie cena nie jest wyższa od poprzedniej o co najmniej 2zł**')
                        logger.warning(f"{msg.author.display_name} próbował przebić o mniej niż 2 zł")
                    except discord.Forbidden:
                        pass
                    return

                if self.data['price'] != self.data['starting_price']:
                    self.data['sum'] = self.data['sum'] - self.data['price'] + new_price
                else:
                    self.data['sum'] = self.data['sum'] + new_price
                self.data['price'] = new_price
                self.data['highest_bidder'] = msg.author.id
                await self.bot.loop.run_in_executor(None, update, self.data)
                await msg.channel.send(f'**{msg.author.mention} podbija cenę do `{new_price} zł`!**')
                logger.info(f'{msg.author.display_name} podbija cenę do {new_price}')

            elif not is_moderator:
                await msg.delete()
                await msg.channel.send(':x: **Aktualnie nie trwa licytacja!**', delete_after=3)
                logger.warning(f"{msg.author.display_name} próbował licytować gdy nie trwała licytacja")

    @tree.command(name="start", description="Rozpocznij licytację")
    async def start(self, ctx, name: str, price: int):

        """Rozpocznij licytację"""

        if auction_organizator_id not in list(map(lambda x: x.id, ctx.user.roles)):
            await ctx.response.send_message(':x: **Nie masz uprawnień do użycia tej komendy!**')
            logger.warning(f"{ctx.user.display_name} próbował rozpocząć licytację")
            return

        if ctx.channel.id != auction_channel:
            await ctx.response.send_message(':x: **Używasz komendy na złym kanale!**')
            logger.warning(f"{ctx.user.display_name} próbował rozpocząć licytację na złym kanale")
            return

        if self.data['running']:
            await ctx.response.send_message(':x: **Licytacja już trwa!**')
            logger.warning(f"{ctx.user.display_name} próbował rozpocząć licytację gdy inna jeszcze trwała")
            return

        self.data['price'] = price
        self.data['name'] = name
        self.data['running'] = True
        self.data['highest_bidder'] = 0
        self.data['starting_price'] = price
        await self.bot.loop.run_in_executor(None, update, self.data)
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=discord.PermissionOverwrite(send_messages=True, read_messages=True))
        await ctx.response.send_message(f':moneybag: **Licytacja `{name}` rozpoczęła się!**\nCena wywoławcza: `{price} zł`')
        logger.info("Start licytacji: *"+ name + "* Cena:" + str(price))

    @tree.command(name="end", description="Zakończ licytację")
    async def end(self, ctx):
        """Zakończ licytację"""

        if auction_organizator_id not in list(map(lambda x: x.id, ctx.user.roles)):
            await ctx.response.send_message(':x: **Nie masz uprawnień do użycia tej komendy!**', ephemeral=True)
            logger.warning(f"{ctx.user.display_name} próbował zakończyć licytację")
            return

        if ctx.channel.id != auction_channel:
            await ctx.response.send_message(':x: **Używasz komendy na złym kanale!**', ephemeral=True)
            logger.warning(f"{ctx.user.display_name} próbował zakończyć licytację na złym kanale")
            return

        if not self.data['running']:
            await ctx.response.send_message(':x: **Nie trwa żadna licytacja!**', ephemeral=True)
            logger.warning(f"{ctx.user.display_name} próbował zakończyć licytację gdy żadna nie trwała")
            return

        self.data['running'] = False
        await self.bot.loop.run_in_executor(None, update, self.data)
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=discord.PermissionOverwrite(send_messages=False, read_messages=True))
        if self.data['highest_bidder'] != 0:
            await ctx.response.send_message(f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n:tada: **Licytacja zakończyła się!** :tada:\n"
                                            f"{ctx.guild.get_member(self.data['highest_bidder']).mention} "
                                            f"kupił(a) `{self.data['name']}` za `{self.data['price']} zł`!")
            logger.info(f"Licytacja zakończyła się: {ctx.guild.get_member(self.data['highest_bidder']).display_name} "
                        f"kupił {self.data['name']} za {self.data['price']}")
        else:
            await ctx.response.send_message(f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n**Licytacja zakończyła się!**\nNikt nie wylicytował przedmiotu")
            logger.info("Licytacja zakończyła się, nikt nie wylicytował przedmiotu")
