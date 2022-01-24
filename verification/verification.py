from discord.ext import commands
from discord.commands import permissions

from .application_buttons import *


class Verification(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        view = discord.ui.View(timeout=None)
        view.add_item(VerifyStudentButton(self.bot))
        view.add_item(VerifyGraduateButton(self.bot))
        view.add_item(VerifyTeacherButton())
        self.bot.add_view(view)

        guild = self.bot.get_guild(801763888633872384)
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
    @permissions.is_user(264815900316794882)
    async def post(self, ctx):
        await ctx.message.delete()
        view = discord.ui.View(timeout=None)
        view.add_item(VerifyStudentButton(self.bot))
        view.add_item(VerifyGraduateButton(self.bot))
        view.add_item(VerifyTeacherButton())

        text = '**Witaj w systemie weryfikacji uczestników V Wielkiej Licytacji PLOPł dla WOŚP. Cieszymy się, że grasz z nami!\n\n' \
               'Aby się zweryfikować, wybierz swoją kategorię wciskając odpowiedni przycisk:**'
        embed = discord.Embed(description=text, colour=0x001437)
        embed.set_image(url='https://i.imgur.com/NeJeNAV.png')

        await ctx.send(embed=embed, view=view)
