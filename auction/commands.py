import discord
from discord.ext import commands
import json


def update(data):
    open('auction/data.json', 'w+', encoding='UTF-8').write(json.dumps(data))
    open('auction/price.txt', 'w+', encoding='UTF-8').write(str(data['price']) + 'zł')
    open('auction/sum.txt', 'w+', encoding='UTF-8').write(str(data['sum']) + 'zł')


class Auction(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = json.loads(open('auction/data.json', 'r+').read())

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.channel.id == 934793332985593856 and msg.author.id != self.bot.user.id:
            is_moderator = 803661290094460938 in list(map(lambda x: x.id, msg.author.roles))

            try:
                new_price = int(msg.content.lower().replace('zł', '').replace('pln', '').replace('zl', '').replace('!', ''))
            except (ValueError, TypeError):
                if not is_moderator:
                    await msg.delete()
                return

            if self.data['running']:
                if new_price > 9000:
                    await self.bot.get_channel(802941824603389982).send(f'{msg.author.mention} próbował/a podbić cenę o {new_price}')
                    await msg.delete()
                    return

                if new_price < self.data['price'] + 2:
                    await msg.delete()
                    try:
                        await msg.author.send(':x: **Podana przez ciebie cena nie jest wyższa od poprzedniej o co najmniej 2zł**')
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

            elif not is_moderator:
                await msg.delete()
                await msg.channel.send(':x: **Aktualnie nie trwa licytacja!**', delete_after=3)

    @commands.slash_command()
    async def start(self, ctx,
                    name: discord.Option(str, 'Nazwa przedmiotu licytacji', label='nazwa'),
                    price: discord.Option(int, 'Cena wywoławcza', label='cena wywoławcza')):
        """Rozpocznij licytację"""

        if 803661290094460938 not in list(map(lambda x: x.id, ctx.author.roles)):
            await ctx.respond(':x: **Nie masz uprawnień do użycia tej komendy!**', ephemeral=True)
            return

        if ctx.channel.id != 934793332985593856:
            await ctx.respond(':x: **Używasz komendy na złym kanale!**', ephemeral=True)
            return

        if self.data['running']:
            await ctx.respond(':x: **Licytacja już trwa!**', ephemeral=True)
            return

        self.data['price'] = price
        self.data['name'] = name
        self.data['running'] = True
        self.data['highest_bidder'] = 0
        self.data['starting_price'] = price
        await self.bot.loop.run_in_executor(None, update, self.data)
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=discord.PermissionOverwrite(send_messages=True, read_messages=False))
        await ctx.respond(f':moneybag: **Licytacja `{name}` rozpoczęła się!**\nCena wywoławcza: `{price} zł`')

    @commands.slash_command()
    async def end(self, ctx):
        """Zakończ licytację"""

        if 803661290094460938 not in list(map(lambda x: x.id, ctx.author.roles)):
            await ctx.respond(':x: **Nie masz uprawnień do użycia tej komendy!**', ephemeral=True)
            return

        if ctx.channel.id != 934793332985593856:
            await ctx.respond(':x: **Używasz komendy na złym kanale!**', ephemeral=True)
            return

        if not self.data['running']:
            await ctx.respond(':x: **Nie trwa żadna licytacja!**', ephemeral=True)
            return

        self.data['running'] = False
        await self.bot.loop.run_in_executor(None, update, self.data)
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=discord.PermissionOverwrite(send_messages=False, read_messages=False))
        if self.data['highest_bidder'] != 0:
            await ctx.respond(f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n:tada: **Licytacja zakończyła się!** :tada:\n{ctx.guild.get_member(self.data['highest_bidder']).mention} kupił(a) `{self.data['name']}` za `{self.data['price']} zł`!")
        else:
            await ctx.respond(f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n**Licytacja zakończyła się!**\nNikt nie wylicytował przedmiotu")
