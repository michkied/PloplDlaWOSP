import pathlib
from logzero import logger
from discord.ext import commands
import json
from ..config import *

path = str(pathlib.Path(__file__).parent.absolute())


class Auction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stop_timer = False
        with open(path + '\\data.json', 'r+', encoding="UTF-8") as f:
            self.data = json.loads(f.read())[0]
        with open(path + '\\history.json', 'r+', encoding="UTF-8") as f:
            history = json.loads(f.read())
            self.history = {int(price): history[price] for price in history}

    async def get_prices(self, ctx: discord.AutocompleteContext):
        return sorted(self.history.keys(), reverse=True)

    def clear_history(self):
        self.history = {}
        with open(path + r"\\history.json", "w+", encoding="UTF-8") as f:
            f.write('{}')

    def update_files(self, data):
        with open(path + r'\\data.json', 'w+', encoding='UTF-8') as f:
            f.write(json.dumps([data], indent=4))

        if str(data['price']) in self.history:
            self.history.pop(str(data['price']))
        self.history[data['price']] = dict(
            filter(lambda x: x[0] in ['highest_bidder', 'sum', 'last_bid_msg'], data.items())
        )
        with open(path + r'\\history.json', "w+", encoding='UTF-8') as f:
            f.write(json.dumps(self.history, indent=4))

    @commands.Cog.listener()
    async def on_message(self, msg):

        if msg.channel.id != AUCTION_CHANNEL or msg.author.id == self.bot.user.id:
            return

        is_moderator = ORGANIZER_ROLE in list(map(lambda x: x.id, msg.author.roles))

        try:
            new_price = int(msg.content.lower().replace('zł', '').replace('pln', '').replace('zl', '').replace('!', ''))
        except (ValueError, TypeError):
            if not is_moderator:
                await msg.delete()
                logger.warning(f"{msg.author.display_name} napisał {msg.content}")
            return

        if not self.data['running']:
            if is_moderator:
                return
            await msg.delete()
            await msg.channel.send(':x: **Aktualnie nie trwa licytacja!**', delete_after=3)
            logger.warning(f"{msg.author.display_name} próbował licytować gdy nie trwała licytacja")
            return

        if new_price - self.data['price'] > 9000:
            await self.bot.get_channel(LOG_CHANNEL).send(f'{msg.author.mention} próbował/a podbić cenę '
                                                         f'o {new_price - self.data["price"]}')
            await msg.delete()
            logger.warning(f"{msg.author.display_name} próbował podbić cenę o {new_price - self.data['price']}")
            return

        if self.data['highest_bidder']:
            diff_err_text = ':x: **Podana przez ciebie cena nie jest wyższa od poprzedniej o co najmniej 2 zł**'
            diff = 2
        else:
            diff_err_text = ':x: **Podana przez ciebie cena jest niższa od ceny wywoławczej**'
            diff = 0
        if self.data['price'] >= 1000:
            diff_err_text = ':x: **Podana przez ciebie cena nie jest wyższa od poprzedniej o co najmniej 5 zł**\n' \
                   ':warning: Po przekroczeniu kwoty 1000 zł mnimalna kwota przebicia wynosi 5 zł'
            diff = 5

        diff_info = ''
        if self.data['price'] < 1000 <= new_price:
            diff_info = '\n\n**WOAH! Mamy 1000 złotych!** :partying_face:\n' \
                         'Pora wytoczyć ciężkie działa - **od teraz przebijamy o minimum 5 zł!**'

        if new_price < self.data['price'] + diff:
            await msg.delete()
            logger.warning(f"{msg.author.display_name} próbował przebić o {new_price}")
            try:
                await msg.author.send(diff_err_text)
            except discord.Forbidden:
                pass
            return

        if self.data['price'] != self.data['starting_price']:
            self.data['sum'] = self.data['sum'] - self.data['price'] + new_price
        else:
            self.data['sum'] = self.data['sum'] + new_price
        self.data['price'] = new_price
        self.data['highest_bidder'] = msg.author.id
        self.data['last_bid_msg'] = f'{msg.author.display_name} podbija do {new_price} zł!'
        self.stop_timer = True

        await self.bot.loop.run_in_executor(None, self.update_files, self.data)
        await msg.channel.send(f'**{msg.author.mention} podbija cenę do `{new_price} zł`!**{diff_info}')
        logger.info(f'{msg.author.display_name} podbija cenę do {new_price}')

    @commands.slash_command()
    async def start(self, ctx, name: str, price: int):
        """Rozpocznij licytację"""

        if ORGANIZER_ROLE not in list(map(lambda x: x.id, ctx.user.roles)):
            await ctx.response.send_message(':x: **Nie masz uprawnień do użycia tej komendy!**', ephemeral=True)
            logger.warning(f"{ctx.user.display_name} próbował rozpocząć licytację")
            return

        if ctx.channel.id != AUCTION_CHANNEL:
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
        self.data['last_bid_msg'] = f'Licytacja rozpoczęta! Cena wywoławcza: {price} zł'
        await self.bot.loop.run_in_executor(None, self.clear_history)
        await self.bot.loop.run_in_executor(None, self.update_files, self.data)
        # await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=discord.PermissionOverwrite(send_messages=True))
        await ctx.response.send_message(f':moneybag: **Licytacja `{name}` rozpoczęła się!**\nCena wywoławcza: `{price} zł`')
        logger.info("Start licytacji: *" + name + "* Cena:" + str(price))

    @commands.slash_command()
    async def end(self, ctx, duration: discord.commands.Option(int, default=20)):
        """Zakończ licytację po opływie określonego czasu"""

        if ORGANIZER_ROLE not in list(map(lambda x: x.id, ctx.user.roles)):
            await ctx.response.send_message(':x: **Nie masz uprawnień do użycia tej komendy!**', ephemeral=True)
            logger.warning(f"{ctx.user.display_name} próbował zakończyć licytację")
            return

        if ctx.channel.id != AUCTION_CHANNEL:
            await ctx.response.send_message(':x: **Używasz komendy na złym kanale!**', ephemeral=True)
            logger.warning(f"{ctx.user.display_name} próbował zakończyć licytację na złym kanale")
            return

        if not self.data['running']:
            await ctx.response.send_message(':x: **Nie trwa żadna licytacja!**', ephemeral=True)
            logger.warning(f"{ctx.user.display_name} próbował zakończyć licytację gdy żadna nie trwała")
            return

        await ctx.response.send_message(f"**Do końca licytacji zostało {duration} sekund!**")
        self.stop_timer = False
        while True:
            duration -= 1

            if duration == 20:
                await ctx.interaction.edit_original_message(content=f"**Do końca licytacji zostało {duration} sekund!**")
            elif duration == 15:
                await ctx.interaction.edit_original_message(content=f"**Do końca licytacji zostało {duration} sekund!**")
            elif duration == 10:
                await ctx.interaction.edit_original_message(content=f"**Do końca licytacji zostało 10 sekund!**")
            elif 5 <= duration <= 10:
                await ctx.interaction.edit_original_message(content=f"**Do końca licytacji zostało {duration} sekund!**")
            elif 2 <= duration <= 4:
                await ctx.interaction.edit_original_message(content=f"**Do końca licytacji zostały {duration} sekundy!**")
            elif duration == 1:
                await ctx.interaction.edit_original_message(content=f"**Do końca licytacji została {duration} sekunda!**")
            elif duration == 0:
                break
            if self.stop_timer == True:
                await ctx.interaction.delete_original_message()
                return

            await asyncio.sleep(1)
        self.data['running'] = False
        # await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=discord.PermissionOverwrite(send_messages=False))
        if self.data['highest_bidder'] != 0:
            highest_bidder = ctx.guild.get_member(self.data['highest_bidder'])
            await ctx.interaction.edit_original_message(content=f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n:tada: **Licytacja zakończyła się!** :tada:\n"
                                            f"{highest_bidder.mention} "
                                            f"kupił(a) `{self.data['name']}` za `{self.data['price']} zł`!")
            self.data['last_bid_msg'] = f"Sprzedane za {self.data['price']} zł!"
            logger.info(f"Licytacja zakończyła się: {highest_bidder.display_name} "
                        f"kupił {self.data['name']} za {self.data['price']}")
        else:
            await ctx.interaction.edit_original_message(content=
                f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n**Licytacja zakończyła się!**\nNikt nie wylicytował przedmiotu")
            self.data['last_bid_msg'] = 'Licytacja zakończona! Nikt nie wylicytował przedmiotu'
            logger.info("Licytacja zakończyła się, nikt nie wylicytował przedmiotu")

        await self.bot.loop.run_in_executor(None, self.update_files, self.data)
        await asyncio.sleep(20)
        self.data['last_bid_msg'] = ''
        self.data['name'] = ''
        self.data['price'] = 0
        await self.bot.loop.run_in_executor(None, self.update_files, self.data)

    @commands.slash_command()
    async def forceend(self, ctx):
        """Natychmiast zakończ licytację"""

        if ORGANIZER_ROLE not in list(map(lambda x: x.id, ctx.user.roles)):
            await ctx.response.send_message(':x: **Nie masz uprawnień do użycia tej komendy!**', ephemeral=True)
            logger.warning(f"{ctx.user.display_name} próbował zakończyć licytację")
            return

        if ctx.channel.id != AUCTION_CHANNEL:
            await ctx.response.send_message(':x: **Używasz komendy na złym kanale!**', ephemeral=True)
            logger.warning(f"{ctx.user.display_name} próbował zakończyć licytację na złym kanale")
            return

        if not self.data['running']:
            await ctx.response.send_message(':x: **Nie trwa żadna licytacja!**', ephemeral=True)
            logger.warning(f"{ctx.user.display_name} próbował zakończyć licytację gdy żadna nie trwała")
            return

        self.stop_timer = True
        self.data['running'] = False
        # await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=discord.PermissionOverwrite(send_messages=False))
        if self.data['highest_bidder'] != 0:
            highest_bidder = ctx.guild.get_member(self.data['highest_bidder'])
            await ctx.response.send_message(f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n:tada: **Licytacja zakończyła się!** :tada:\n"
                                            f"{highest_bidder.mention} "
                                            f"kupił(a) `{self.data['name']}` za `{self.data['price']} zł`!")
            self.data['last_bid_msg'] = f"Sprzedane za {self.data['price']} zł!"
            logger.info(f"Licytacja zakończyła się: {highest_bidder.display_name} "
                        f"kupił {self.data['name']} za {self.data['price']}")
        else:
            await ctx.response.send_message(
                f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n**Licytacja zakończyła się!**\nNikt nie wylicytował przedmiotu")
            self.data['last_bid_msg'] = 'Licytacja zakończona! Nikt nie wylicytował przedmiotu'
            logger.info("Licytacja zakończyła się, nikt nie wylicytował przedmiotu")

        await self.bot.loop.run_in_executor(None, self.update_files, self.data)
        await asyncio.sleep(20)
        self.data['last_bid_msg'] = ''
        self.data['name'] = ''
        self.data['price'] = 0
        await self.bot.loop.run_in_executor(None, self.update_files, self.data)

    @commands.slash_command()
    async def pause(self, ctx):
        if ORGANIZER_ROLE not in list(map(lambda x: x.id, ctx.user.roles)):
            await ctx.response.send_message(':x: **Nie masz uprawnień do użycia tej komendy!**', ephemeral=True)
            logger.warning(f"{ctx.user.display_name} próbował wstrzymać licytację")
            return

        if ctx.channel.id != AUCTION_CHANNEL:
            await ctx.response.send_message(':x: **Używasz komendy na złym kanale!**', ephemeral=True)
            logger.warning(f"{ctx.user.display_name} próbował wstrzymać licytację na złym kanale")
            return

        if not self.data['running']:
            await ctx.response.send_message(':x: **Nie trwa żadna licytacja!**', ephemeral=True)
            logger.warning(f"{ctx.user.display_name} próbował wstrzymać licytację gdy żadna nie trwała")
            return

        self.stop_timer = True
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=discord.PermissionOverwrite(send_messages=False))
        await ctx.response.send_message(f":warning: **Licytacja wstrzymana!**")

    @commands.slash_command()
    async def unpause(self, ctx):
        if ORGANIZER_ROLE not in list(map(lambda x: x.id, ctx.user.roles)):
            await ctx.response.send_message(':x: **Nie masz uprawnień do użycia tej komendy!**', ephemeral=True)
            logger.warning(f"{ctx.user.display_name} próbował wznowić licytację")
            return

        if ctx.channel.id != AUCTION_CHANNEL:
            await ctx.response.send_message(':x: **Używasz komendy na złym kanale!**', ephemeral=True)
            logger.warning(f"{ctx.user.display_name} próbował wznowić licytację na złym kanale")
            return

        if not self.data['running']:
            await ctx.response.send_message(':x: **Nie trwa żadna licytacja!**', ephemeral=True)
            logger.warning(f"{ctx.user.display_name} próbował wznowić licytację gdy żadna nie trwała")
            return

        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=discord.PermissionOverwrite(send_messages=True))
        await ctx.response.send_message(f":tada: **Licytacja wznowiona!**")

    @commands.slash_command()
    async def revert(self, ctx,
                     price: discord.Option(
                         int, "Cena, do której cofnąć licytację",
                         name="cena", autocomplete=get_prices
                     )):
        if ORGANIZER_ROLE not in list(map(lambda x: x.id, ctx.user.roles)):
            await ctx.response.send_message(':x: **Nie masz uprawnień do użycia tej komendy!**', ephemeral=True)
            logger.warning(f"{ctx.user.display_name} próbował cofnąć licytację")
            return

        if ctx.channel.id != AUCTION_CHANNEL:
            await ctx.response.send_message(':x: **Używasz komendy na złym kanale!**', ephemeral=True)
            logger.warning(f"{ctx.user.display_name} próbował cofnąć licytację na złym kanale")
            return

        if not self.data['running']:
            await ctx.response.send_message(':x: **Nie trwa żadna licytacja!**', ephemeral=True)
            logger.warning(f"{ctx.user.display_name} próbował cofnąć licytację gdy żadna nie trwała")
            return

        to_del = []
        for bid in self.history:
            if bid > price:
                to_del.append(bid)
        for bid in to_del:
            self.history.pop(bid)

        self.data['price'] = price
        self.data['highest_bidder'] = self.history[price]['highest_bidder']
        self.data['sum'] = self.history[price]['sum']
        self.data['last_bid_msg'] = self.history[price]['last_bid_msg']
        await self.bot.loop.run_in_executor(None, self.update_files, self.data)
        if self.data['highest_bidder'] != 0:
            text = f':warning: **Licytacja została cofnięta do wcześniejszego stanu**\n' \
                   f'Aktualną kwotą jest `{price} zł` od **<@{self.data["highest_bidder"]}>**'
        else:
            text = f':warning: **Licytacja została cofnięta do kwoty wywoławczej - `{price} zł`**'

        await ctx.response.send_message(text)

    @commands.slash_command()
    async def say(self, ctx, message: str):

        if ORGANIZER_ROLE not in list(map(lambda x: x.id, ctx.user.roles)):
            await ctx.response.send_message(':x: **Nie masz uprawnień do użycia tej komendy!**', ephemeral=True)
            logger.warning(f"{ctx.user.display_name} próbował użyć komenmdy /say")
            return

        await ctx.channel.send(message)
        await ctx.response.send_message("Wysłano.", ephemeral=True)
        await ctx.interaction.delete_original_message()