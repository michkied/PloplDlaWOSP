import requests
from discord.ext import commands
from .application_buttons import *
from ..config import *

path = str(pathlib.Path(__file__).parent.absolute())


def download(url):
    r = requests.get(url)
    open(os.path.join(path, f"img.{url.split('.')[-1]}"), 'wb').write(r.content)


class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        with open(os.path.join(path, 'student_keys.json'), 'r+', encoding='UTF-8') as f:
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

        extension = VERIFICATION_IMAGE_URL.split('.')[-1]
        if not os.path.exists(os.path.join(path, f'img.{extension}')):
            logger.info("Obraz do wiadomości Post nie został pobrany. Pobieranie...")
            await self.bot.loop.run_in_executor(None, download, VERIFICATION_IMAGE_URL)
            logger.info("Pobrano.")

        await ctx.send(file=discord.File(os.path.join(path, f'img.{extension}')))
        text = ('# Siema!\n'
                '**Witaj w systemie weryfikacji uczestników VII Wielkiej Licytacji PLOPŁ dla WOŚP!**\n'
                'Cieszymy się, że grasz z nami! :tada:\n'
                '### Aby się zweryfikować, wybierz swoją kategorię wciskając odpowiedni przycisk:')
        await ctx.send(text, view=view)

        logger.info("Wiadomość Post wysłana")
