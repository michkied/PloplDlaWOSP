# PloplDlaWOSP
#
# Made with Python 3.8 & ❤love❤ by Michał Kiedrzyński (michkied#6677)
# 01.2021

import discord
from discord.ext import commands
import json
from datetime import datetime

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='?', intents=intents)
bot.remove_command('help')


def update(data):
    open('data.json', 'w+').write(json.dumps(data))
    open('price.txt', 'w+').write(str(data['price']) + ' PLN')
    open('sum.txt', 'w+').write(str(data['price_sum']) + ' PLN')


@bot.event
async def on_ready():
    date = datetime.now()
    print('Logged in as:')
    print(bot.user.name)
    print(bot.user.id)
    print(date.strftime('%d.%m.%Y  %H:%M'))
    print('by Michał Kiedrzyński')
    print('------')


@bot.event
async def on_message(msg):
    if msg.channel.id == 803730916198318131 and msg.author.id != bot.user.id:
        moderator = 803661290094460938 in list(map(lambda x: x.id, msg.author.roles))
        try:
            value = int(msg.content.lower().replace('zł', '').replace('pln', '').replace('zl', '').replace('!', ''))
        except (ValueError, TypeError):
            if not moderator:
                await msg.delete()
        else:
            if bot.data['running']:
                if bot.data['price'] + 2 > value:
                    await msg.delete()
                    try:
                        await msg.author.send(':x: **Podana przez ciebie cena nie jest wyższa od poprzedniej o co najmniej 2 PLN**')
                    except discord.Forbidden:
                        pass
                else:
                    if bot.data['price'] != bot.data['starting_price']:
                        bot.data['price_sum'] = bot.data['price_sum'] - bot.data['price'] + value
                    else:
                        bot.data['price_sum'] = bot.data['price_sum'] + value
                    bot.data['price'] = value
                    bot.data['highest_bidder'] = msg.author.id
                    await bot.loop.run_in_executor(None, update, bot.data)
                    await msg.channel.send(f'**{msg.author.mention} podbija cenę do `{value} zł`!**')
            elif not moderator:
                await msg.delete()
                await msg.channel.send(':x: **Aktualnie nie trwa licytacja!**', delete_after=3)

    await bot.process_commands(msg)


@bot.command()
async def start(ctx, price=None, *, name=None):
    if ctx.channel.id == 803730916198318131:
        if 803661290094460938 in list(map(lambda x: x.id, ctx.author.roles)):
            if not bot.data['running']:
                try:
                    price = int(price)
                except (ValueError, TypeError):
                    await ctx.message.delete()
                else:
                    await ctx.message.delete()
                    bot.data['price'] = price
                    bot.data['name'] = name
                    bot.data['running'] = True
                    bot.data['highest_bidder'] = 0
                    bot.data['starting_price'] = price
                    await bot.loop.run_in_executor(None, update, bot.data)
                    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=discord.PermissionOverwrite(send_messages=True))
                    await ctx.send(f':moneybag: **Licytacja `{name}` rozpoczęła się!**\nCena wywoławcza: `{price} zł`')

            else:
                await ctx.message.delete()
                await ctx.send(':x: **Licytacja już trwa!**', delete_after=3)


@bot.command()
async def end(ctx):
    if ctx.channel.id == 803730916198318131:
        if 803661290094460938 in list(map(lambda x: x.id, ctx.author.roles)):
            if bot.data['running']:
                await ctx.message.delete()
                bot.data['running'] = False
                await bot.loop.run_in_executor(None, update, bot.data)
                await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=discord.PermissionOverwrite(send_messages=False))
                if bot.data['highest_bidder'] != 0:
                    await ctx.send(f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n:tada: **Licytacja zakończyła się!** :tada:\n{ctx.guild.get_member(bot.data['highest_bidder']).mention} kupił(a) `{bot.data['name']}` za `{bot.data['price']} zł`!")
                else:
                    await ctx.send(f"▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n\n**Licytacja zakończyła się!**\nNikt nie wylicytował przedmiotu")

            else:
                await ctx.message.delete()
                await ctx.send(':x: **Nie trwa żadna licytacja!**', delete_after=3)


if __name__ == '__main__':
    bot.data = json.loads(open('data.json', 'r+').read())

    bot.run('TOKEN', reconnect=True)
