from .decision_buttons import *
from .application_modals import *


class VerifyStudentButton(ui.Button):
    def __init__(self, bot, student_keys):
        self.bot = bot
        self.student_keys = student_keys
        super().__init__(label="🎒 Uczeń", style=discord.enums.ButtonStyle.blurple, custom_id="STU_BUTTON")

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user

        role_ids = map(lambda role: role.id, user.roles)
        if UNVERIFIED_ROLES[0] in role_ids or UNVERIFIED_ROLES[1] in role_ids:
            await interaction.response.send_message(
                ":x: **Cierpliwości!**\nTwoje zgłoszenie już do nas dotarło i jest w trakcie weryfikacji.",
                ephemeral=True
            )
            return

        modal = StudentVerificationModal(self.student_keys)
        await interaction.response.send_modal(modal)
        await modal.wait()
        if modal.children[0].value is None:
            return
        name, clss, key = list(map(lambda _: _.value, modal.children))
        key = key.upper()

        if key not in self.student_keys:
            logger.warning(
                f"Nieudana próba weryfikacji ucznia: {user.display_name} - {name}, Klasa: {clss}, Klucz: {key}"
            )
            text = (f":warning: **Nieudana próba weryfikacji jako uczeń (błędny klucz)** :warning:\n"
                    f"**Użytkownik - {user.mention}**\n\n"
                    f"Podane dane:\n"
                    f"`Imię i nazwisko` - {name}\n"
                    f"`Klasa` - {clss}\n"
                    f"`Klucz weryfikacyjny` - {key}\n\n"
                    f"`Data utworzenia konta` - <t:{int(user.created_at.timestamp())}:F>\n"
                    f"`Data dołączenia do serwera` - <t:{int(user.joined_at.timestamp())}:F>")
            embed = discord.Embed(description=text, color=discord.Color.red())
            await self.bot.get_channel(VERIFICATION_CHANNEL).send(embed=embed)
            return

        try:
            await user.edit(nick=f"{self.student_keys[key][0]} {self.student_keys[key][1]}")
        except discord.Forbidden:
            pass

        if name.lower() == self.student_keys[key][0].lower() and clss.lower() == self.student_keys[key][1].lower():
            logger.info(f"Uczeń: {user.display_name} zweryfikowany przy pomocy klucza")
            text = (f':school_satchel: **Uczeń - {user.mention}**\n'
                    f'`Imię i nazwisko` - {name}\n'
                    f'`Klasa` - {clss}\n'
                    f'`Klucz` - {key}\n\n'
                    f':white_check_mark: **Zweryfikowano automatycznie przy pomocy klucza**')
            embed = discord.Embed(description=text, color=discord.Color.green())
            await self.bot.get_channel(VERIFICATION_CHANNEL).send(embed=embed)
            await user.add_roles(interaction.guild.get_role(VERIFIED_ROLES[0]))
            return

        text = (f':school_satchel: **Uczeń - {user.mention}**\n'
                f'Podane dane:\n'
                f'`Imię i nazwisko` - {name}\n'
                f'`Klasa` - {clss}\n'
                f'`Klucz` - {key}\n\n'
                f'Dane z bazy:\n'
                f'`Imię i nazwisko` - {self.student_keys[key][0]}\n'
                f'`Klasa` - {self.student_keys[key][1]}')
        embed = discord.Embed(description=text, color=discord.Color.yellow())

        view = discord.ui.View(timeout=None)
        view.add_item(ApproveButton(self.bot, user.id, 0))
        view.add_item(DenyButton(self.bot, user.id, 0))

        await self.bot.get_channel(VERIFICATION_CHANNEL).send(embed=embed, view=view)
        await user.add_roles(interaction.guild.get_role(UNVERIFIED_ROLES[0]))


class VerifyGraduateButton(ui.Button):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(label="🎓 Absolwent", style=discord.enums.ButtonStyle.blurple, custom_id="GRD_BUTTON")

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user

        role_ids = map(lambda role: role.id, user.roles)
        if UNVERIFIED_ROLES[0] in role_ids or UNVERIFIED_ROLES[1] in role_ids:
            await interaction.response.send_message(":x: **Cierpliwości!**\nTwoje zgłoszenie już do nas dotarło i jest w trakcie weryfikacji.", ephemeral=True)
            return

        modal = GraduateVerificationModal()
        await interaction.response.send_modal(modal)
        await modal.wait()
        name, year, clss, teacher = list(map(lambda _: _.value, modal.children))
        if modal.children[0].value is None:
            return
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

        await user.edit(nick=name)
        await self.bot.get_channel(VERIFICATION_CHANNEL).send(embed=embed, view=view)
        await user.add_roles(interaction.guild.get_role(UNVERIFIED_ROLES[1]))


class VerifyTeacherButton(ui.Button):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(label="🧑‍🏫 Nauczyciel", style=discord.enums.ButtonStyle.blurple, custom_id="TCH_BUTTON")

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild

        if user.id in TEACHERS:
            logger.info(f"Nauczyciel: {user.display_name} znaleziony na liście ID")
            await user.add_roles(guild.get_role(VERIFIED_ROLES[2]))
            await interaction.response.send_message(":white_check_mark: **Weryfikacja przebiegła pomyślnie!**", ephemeral=True)
            await guild.get_channel(VERIFICATION_CHANNEL).send(
                f':white_check_mark::teacher: **Użytkownik {user.mention} zweryfikował się jako nauczyciel** (lista ID)'
            )
            return

        modal = TeacherVerificationModal()
        await interaction.response.send_modal(modal)
        await modal.wait()
        if modal.children[0].value is None:
            return
        name = modal.children[0].value
        key = modal.children[1].value

        if key != TEACHER_KEY:
            logger.warning(f"Nieudana próba weryfikacji nauczyciela: {user.display_name} - {name}, Klucz: {key}")
            text = f":warning: **Nieudana próba weryfikacji jako nauczyciel** :warning:\n" \
                   f"**Użytkownik - {user.mention}**\n" \
                   f"Imię i nazwisko: {name}\n" \
                   f"Podany kod dostępu: {key}\n\n" \
                   f"Data utworzenia konta: <t:{int(user.created_at.timestamp())}:F>\n" \
                   f"Data dołączenia do serwera: <t:{int(user.joined_at.timestamp())}:F>"

            embed = discord.Embed(description=text, color=discord.Color.red())
            await self.bot.get_channel(VERIFICATION_CHANNEL).send(embed=embed)
            return

        await user.edit(nick=name)
        logger.info(f"Nauczyciel: {user.display_name} zweryfikowany przy pomocy klucza")
        await user.add_roles(guild.get_role(VERIFIED_ROLES[2]))
        await guild.get_channel(VERIFICATION_CHANNEL).send(
            f':white_check_mark::teacher: **Użytkownik {user.mention} zweryfikował się jako nauczyciel** (klucz weryfikacyjny)'
        )
