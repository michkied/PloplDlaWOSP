import pathlib
from logzero import logger
from discord.ext import commands
import json
from ..config import *

path = str(pathlib.Path(__file__).parent.absolute())


class Auction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open(path + '\\data.json', 'r+', encoding="UTF-8") as f:
            self.data = json.loads(f.read())
        with open(path + '\\history.json', 'r+', encoding="UTF-8") as f:
            history = json.loads(f.read())
            self.history = {int(price): history[price] for price in history}

    async def get_prices(self, ctx: discord.AutocompleteContext):
        return sorted(self.history.keys(), reverse=True)

    def clear_history(self):
        self.history = {}
        with open(path + r"\\history.json", "w+") as f:
            f.write('{}')

    def update_files(self, data):
        with open(path + r'\\data.json', 'w+', encoding='UTF-8') as f:
            f.write(json.dumps(data))
        with open(path + r'\\price.txt', 'w+', encoding='UTF-8') as f:
            f.write(str(data['price']) + 'zł')
        with open(path + r'\\sum.txt', 'w+', encoding='UTF-8') as f:
            f.write(str(data['sum']) + 'zł')

        if str(data['price']) in self.history:
            self.history.pop(str(data['price']))
        self.history[data['price']] = dict(
            filter(lambda x: x[0] in ['highest_bidder', 'sum'], data.items())
        )
        with open(path + r'\\history.json', "w+", encoding='UTF-8') as f:
            f.write(json.dumps(self.history, indent=4))

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.channel.id == auction_channel and msg.author.id != self.bot.user.id:
            is_moderator = auction_organizer_id in list(map(lambda x: x.id, msg.author.roles))

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

                if self.data['highest_bidder']:
                    diff = 2
                else:
                    diff = 0

                if new_price < self.data['price'] + diff:
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

                await self.bot.loop.run_in_executor(None, self.update_files, self.data)
                await msg.channel.send(f'**{msg.author.mention} podbija cenę do `{new_price} zł`!**')
                logger.info(f'{msg.author.display_name} podbija cenę do {new_price}')

            elif not is_moderator:
                await msg.delete()
                await msg.channel.send(':x: **Aktualnie nie trwa licytacja!**', delete_after=3)
                logger.warning(f"{msg.author.display_name} próbował licytować gdy nie trwała licytacja")

    @commands.slash_command()
    async def start(self, ctx, name: str, price: int):
        """Rozpocznij licytację"""

        if auction_organizer_id not in list(map(lambda x: x.id, ctx.user.roles)):
            await ctx.response.send_message(':x: **Nie masz uprawnień do użycia tej komendy!**', ephemeral=True)
            logger.warning(f"{ctx.user.display_name} próbował rozpocząć licytację")
            return

        if ctx.channel.id != auction_channel:
            await ctx.response.send_message(':x: **Używasz komendy na złym kanale!**', ephemeral=True)
            logger.warning(f"{ctx.user.display_name} próbował rozpocząć licytację na złym kanale")
            return

        if self.data['running']:
            await ctx.response.send_message(':x: **Licytacja już trwa!**', ephemeral=True)
            logger.warning(f"{ctx.user.display_name} próbował rozpocząć licytację gdy inna jeszcze trwała")
            return

        self.data['price'] = price
        self.data['name'] = name
        self.data['running'] = True
        self.data['highest_bidder'] = 0
        self.data['starting_price'] = price
        await self.bot.loop.run_in_executor(None, self.clear_history)
        await self.bot.loop.run_in_executor(None, self.update_files, self.data)
        # await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=discord.PermissionOverwrite(send_messages=True, read_messages=True))
        await ctx.response.send_message(f':moneybag: **Licytacja `{name}` rozpoczęła się!**\nCena wywoławcza: `{price} zł`')
        logger.info("Start licytacji: *" + name + "* Cena:" + str(price))

    @commands.slash_command()
    async def end(self, ctx):
        """Zakończ licytację"""

        if auction_organizer_id not in list(map(lambda x: x.id, ctx.user.roles)):
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
        await self.bot.loop.run_in_executor(None, self.update_files, self.data)
        # await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=discord.PermissionOverwrite(send_messages=False, read_messages=True))
        if self.data['highest_bidder'] != 0:
            await ctx.response.send_message(f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n:tada: **Licytacja zakończyła się!** :tada:\n"
                                            f"{ctx.guild.get_member(self.data['highest_bidder']).mention} "
                                            f"kupił(a) `{self.data['name']}` za `{self.data['price']} zł`!")
            logger.info(f"Licytacja zakończyła się: {ctx.guild.get_member(self.data['highest_bidder']).display_name} "
                        f"kupił {self.data['name']} za {self.data['price']}")
        else:
            await ctx.response.send_message(f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n**Licytacja zakończyła się!**\nNikt nie wylicytował przedmiotu")
            logger.info("Licytacja zakończyła się, nikt nie wylicytował przedmiotu")

    @commands.slash_command()
    async def revert(self, ctx,
                     price: discord.Option(
                         int, "Cena, do której cofnąć licytację",
                         name="cena", autocomplete=get_prices
                     )):

        to_del = []
        for bid in self.history:
            if bid > price:
                to_del.append(bid)
        for bid in to_del:
            self.history.pop(bid)

        self.data['price'] = price
        self.data['highest_bidder'] = self.history[price]['highest_bidder']
        self.data['sum'] = self.history[price]['sum']
        await self.bot.loop.run_in_executor(None, self.update_files, self.data)
        if self.data['highest_bidder'] != 0:
            text = f':warning: **Licytacja została cofnięta do wcześniejszego stanu**\n' \
                   f'Aktualną kwotą jest `{price} zł` od **<@{self.data["highest_bidder"]}>**'
        else:
            text = f':warning: **Licytacja została cofnięta do kwoty wywoławczej - `{price} zł`**'

        await ctx.response.send_message(text)