import json
import pathlib
from discord.ext import commands
from .application_buttons import *
from ..config import *

path = str(pathlib.Path(__file__).parent.absolute())


class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open(path + r'\\student_keys.json', 'r+', encoding='UTF-8') as f:
            self.student_keys = json.loads(f.read())

    @commands.Cog.listener()
    async def on_ready(self):
        view = discord.ui.View(timeout=None)
        view.add_item(VerifyStudentButton(self.bot, self.student_keys))
        view.add_item(VerifyGraduateButton(self.bot))
        view.add_item(VerifyTeacherButton(self.bot))
        self.bot.add_view(view)

        guild = self.bot.get_guild(AUCTION_GUILD)
        unverified = {
            0: guild.get_role(UNVERIFIED_ROLES[0]).members,
            1: guild.get_role(UNVERIFIED_ROLES[1]).members
        }

        for user_type in unverified:
            for user in unverified[user_type]:
                view = discord.ui.View(timeout=None)
                view.add_item(ApproveButton(self.bot, user.id, user_type))
                view.add_item(DenyButton(self.bot, user.id, user_type))
                self.bot.add_view(view)

    @commands.command()
    async def post(self, ctx):
        if ORGANIZER_ROLE not in map(lambda role: role.id, ctx.author.roles):
            return
        await ctx.message.delete()
        view = discord.ui.View(timeout=None)
        view.add_item(VerifyStudentButton(self.bot, self.student_keys))
        view.add_item(VerifyGraduateButton(self.bot))
        view.add_item(VerifyTeacherButton(self.bot))

        text = '**Witaj w systemie weryfikacji uczestników VII Wielkiej Licytacji PLOPŁ dla WOŚP!\n\n' \
               'Aby się zweryfikować, wybierz swoją kategorię wciskając odpowiedni przycisk:**'
        embed = discord.Embed(description=text, colour=0x001437)
        embed.set_image(url=VERIFICATION_IMAGE_URL)

        await ctx.send(embed=embed, view=view)
        logger.info("Wiadomość Post wysłana")
