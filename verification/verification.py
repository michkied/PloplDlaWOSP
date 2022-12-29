from discord.ext import commands
from .application_buttons import *
from .config import *


class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        view = discord.ui.View(timeout=None)
        view.add_item(VerifyStudentButton(self.bot))
        view.add_item(VerifyGraduateButton(self.bot))
        view.add_item(VerifyTeacherButton())
        self.bot.add_view(view)

        guild = self.bot.get_guild(server_id)
        unverified = {
            0: guild.get_role(unverified_roles[0]).members,
            1: guild.get_role(unverified_roles[1]).members
        }

        for user_type in unverified:
            for user in unverified[user_type]:
                view = discord.ui.View(timeout=None)
                view.add_item(ApproveButton(self.bot, user.id, user_type))
                view.add_item(DenyButton(self.bot, user.id, user_type))
                self.bot.add_view(view)

    @commands.command()
    async def post(self, ctx):
        await ctx.message.delete()
        view = discord.ui.View(timeout=None)
        view.add_item(VerifyStudentButton(self.bot))
        view.add_item(VerifyGraduateButton(self.bot))
        view.add_item(VerifyTeacherButton(self.bot))

        text = '**Witaj w systemie weryfikacji uczestników Debaty 2022-2023\n\n' \
               'Aby się zweryfikować, wybierz swoją kategorię wciskając odpowiedni przycisk:**'
        embed = discord.Embed(description=text, colour=0x001437)
        # embed.set_image(url='https://i.imgur.com/NeJeNAV.png')

        await ctx.send(embed=embed, view=view)
        logger.info("Wiadomość Post wysłana")

    @commands.Cog.listener()
    async def on_message(self, msg):
        if "?post" not in msg.content.lower() and msg.channel.id == only_verification_channel and \
                msg.author.id != self.bot.user.id:
            await msg.delete()
