from .decision_buttons import *
from .application_modals import *


class VerifyStudentButton(ui.Button):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(label="🎒 Uczeń", style=discord.enums.ButtonStyle.blurple, custom_id="STU_BUTTON")

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user

        role_ids = map(lambda role: role.id, user.roles)
        if unverified_roles[0] in role_ids or unverified_roles[1] in role_ids:
            await interaction.response.send_message(
                ":x: **Cierpliwości!**\nTwoje zgłoszenie już do nas dotarło i jest w trakcie weryfikacji.",
                ephemeral=True
            )
            return

        modal = StudentVerificationModal()
        await interaction.response.send_modal(modal)
        await modal.wait()
        username = f'{modal.children[0].value} {modal.children[1].value.upper()}'

        logger.info(f"Uczeń: {user.display_name} Podany nick: {username}")

        await user.edit(nick=username)

        if user.id not in users_data:
            other_guilds = ':warning: **Użytkownika nie ma na żadnym serwerze klasowym**'
        else:
            other_guilds = '`Na innych serwerach:`\n'
            for guild in users_data[user.id]:
                other_guilds += f'{guild["guild"]}  -  {guild["nick"]}\n'

        text = f'**Uczeń - {user.mention}**\n' \
               f'`Podane dane` - {username}\n\n' \
               f'{other_guilds}'
        embed = discord.Embed(description=text, color=discord.Color.blurple())

        view = discord.ui.View(timeout=None)
        view.add_item(ApproveButton(self.bot, user.id, 0))
        view.add_item(DenyButton(self.bot, user.id, 0))

        await self.bot.get_channel(applications_channel).send(embed=embed, view=view)
        await user.add_roles(interaction.guild.get_role(unverified_roles[0]))


class VerifyGraduateButton(ui.Button):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(label="🎓 Absolwent", style=discord.enums.ButtonStyle.blurple, custom_id="GRD_BUTTON")

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user

        role_ids = map(lambda role: role.id, user.roles)
        if unverified_roles[0] in role_ids or unverified_roles[1] in role_ids:
            await interaction.response.send_message(":x: **Cierpliwości!**\nTwoje zgłoszenie już do nas dotarło i jest w trakcie weryfikacji.", ephemeral=True)
            return

        modal = GraduateVerificationModal()
        await interaction.response.send_modal(modal)
        await modal.wait()
        name, year, clss, teacher = list(map(lambda _: _.value, modal.children))
        clss = clss.upper()

        text = f'**Absolwent - {user.mention}**\n' \
               f'`Imię` - {name}\n' \
               f'`Klasa` - {clss}\n' \
               f'`Rok ukończenia` - {year}\n' \
               f'`Wychowawca` - {teacher}'
        embed = discord.Embed(description=text, color=discord.Color.blurple())

        logger.info(f"Absolwent: {user.display_name}, Imię: {name}, Klasa: {clss}, Rok ukończenia: {year}, Wychowawca: "
                    f"{teacher}")

        view = discord.ui.View(timeout=None)
        view.add_item(ApproveButton(self.bot, user.id, 1))
        view.add_item(DenyButton(self.bot, user.id, 1))

        await self.bot.get_channel(applications_channel).send(embed=embed, view=view)
        await user.add_roles(interaction.guild.get_role(unverified_roles[1]))


class VerifyTeacherButton(ui.Button):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(label="🧑‍🏫 Nauczyciel", style=discord.enums.ButtonStyle.blurple, custom_id="TCH_BUTTON")

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild

        if user.id in teachers:
            logger.info(f"Nauczyciel: {user.display_name} znaleziony na liście ID")
            await user.add_roles(guild.get_role(verified_roles[2]))
            await interaction.response.send_message(":white_check_mark: **Weryfikacja przebiegła pomyślnie!**", ephemeral=True)
            await guild.get_channel(applications_channel).send(
                f':white_check_mark::teacher: **Użytkownik {user.mention} zweryfikował się jako nauczyciel** (lista ID)'
            )
            return

        modal = TeacherVerificationModal()
        await interaction.response.send_modal(modal)
        await modal.wait()
        name = modal.children[0].value
        key = modal.children[1].value

        if key != TEACHER_KEY:
            logger.warning(f"Nieudana próba weryfikacji nauczyciela: {user.display_name} - {name}, Kod dostępu: {key}")
            text = f":warning: **Nieudana próba weryfikacji jako nauczyciel** :warning:\n" \
                   f"**Użytkownik - {user.mention}**\n" \
                   f"Imię i nazwisko: {name}\n" \
                   f"Podany kod dostępu: {key}\n\n" \
                   f"Data utworzenia konta: <t:{int(user.created_at.timestamp())}:F>\n" \
                   f"Data dołączenia do serwera: <t:{int(user.joined_at.timestamp())}:F>"

            embed = discord.Embed(description=text, color=discord.Color.red())
            await self.bot.get_channel(applications_channel).send(embed=embed)
            return

        await user.edit(nick=name)
        logger.info(f"Nauczyciel: {user.display_name} zweryfikowany przy pomocy kodu")
        await user.add_roles(guild.get_role(verified_roles[2]))
        await guild.get_channel(applications_channel).send(
            f':white_check_mark::teacher: **Użytkownik {user.mention} zweryfikował się jako nauczyciel** (kod dostępu)'
        )
