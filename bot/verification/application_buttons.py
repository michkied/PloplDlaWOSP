from .decision_buttons import *
from .application_modals import *


class VerifyStudentButton(ui.Button):
    def __init__(self, bot, student_keys):
        self.bot = bot
        self.student_keys = student_keys
        super().__init__(label="🎒 Uczeń", style=discord.enums.ButtonStyle.blurple, custom_id="STU_BUTTON")

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user

        role_ids = list(map(lambda role: role.id, user.roles))
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
        name, clss, num, key = list(map(lambda _: _.value, modal.children))
        key = key.upper()

        if key not in self.student_keys:
            logger.warning(
                f"Nieudana próba weryfikacji ucznia: {user.display_name} - {name}, "
                f"Klasa: {clss}, Numer {num}, Klucz: {key}"
            )
            text = (f":school_satchel: **Uczeń - {user.mention}**\n\n"
                    f"**Podane dane:**\n"
                    f"Imię i nazwisko: `{name}`\n"
                    f"Klasa: `{clss}`\n"
                    f"Numer z dziennika: `{num}`\n"
                    f"Klucz: `{key}`\n\n"
                    f"Data utworzenia konta: <t:{int(user.created_at.timestamp())}:F>\n"
                    f"Data dołączenia do serwera: <t:{int(user.joined_at.timestamp())}:F>\n\n"
                    f":x: **Odrzucono automatycznie** (błędny klucz)")
            embed = discord.Embed(description=text, color=discord.Color.red())
            await self.bot.get_channel(VERIFICATION_CHANNEL).send(embed=embed)
            return

        try:
            await user.edit(nick=f"{name} {clss.upper()}")
        except discord.Forbidden:
            pass

        data = self.student_keys[key]
        if name.lower() == data[0].lower() and clss.lower() == data[1].lower() and num == data[2]:
            logger.info(f"Uczeń: {user.display_name} zweryfikowany przy pomocy klucza")
            text = (f':school_satchel: **Uczeń - {user.mention}**\n'
                    f'Imię i nazwisko: `{name}`\n'
                    f'Klasa: `{clss}`\n'
                    f'Numer z dziennika: `{num}`\n'
                    f'Klucz: `{key}`\n\n'
                    f':white_check_mark: **Zweryfikowano automatycznie** (klucz weryfikacyjny)')
            embed = discord.Embed(description=text, color=discord.Color.green())
            await self.bot.get_channel(VERIFICATION_CHANNEL).send(embed=embed)
            await user.add_roles(interaction.guild.get_role(VERIFIED_ROLES[0]))
            return

        old_guild = self.bot.get_guild(OLD_GUILD)
        old_member = old_guild.get_member(user.id)
        old_student_role = old_guild.get_role(OLD_VERIFIED_ROLES[0])
        if old_member is not None:
            old_guild_text = (
                f'**Dane ze starego serwera:**\n'
                f'Zweryfikowany jako uczeń? `{"Tak" if old_student_role in old_member.roles else "Nie"}`\n'
                f'Nick: `{old_member.display_name}`\n'
            )
        else:
            old_guild_text = '*Użytkownika nie ma na starym serwerze*'

        text = (f':school_satchel: **Uczeń - {user.mention}**\n\n'
                f'**Podane dane:**\n'
                f'Imię i nazwisko: `{name}`\n'
                f'Klasa: `{clss}`\n'
                f'Numer z dziennika: `{num}`\n'
                f'Klucz: `{key}`\n\n'
                f'**Dane z bazy:**\n'
                f'Imię i nazwisko: `{data[0]}`\n'
                f'Klasa: `{data[1]}`\n'
                f'Numer z dziennika: `{data[2]}`\n\n'
                f'{old_guild_text}')
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

        role_ids = list(map(lambda role: role.id, user.roles))
        if UNVERIFIED_ROLES[0] in role_ids or UNVERIFIED_ROLES[1] in role_ids:
            await interaction.response.send_message(
                ":x: **Cierpliwości!**\nTwoje zgłoszenie już do nas dotarło i jest w trakcie weryfikacji.",
                ephemeral=True
            )
            return

        old_guild = self.bot.get_guild(OLD_GUILD)
        old_member = old_guild.get_member(user.id)
        if old_member is not None:
            if old_guild.get_role(OLD_VERIFIED_ROLES[1]) in old_member.roles:
                await interaction.response.send_message(
                    ":white_check_mark: **Weryfikacja przebiegła pomyślnie!**", ephemeral=True
                )
                logger.info(f"Absolwent: {user.display_name} zweryfikowany przez obecność na starym serwerze")
                text = (f':mortar_board: **Absolwent - {user.mention}**\n\n'
                        f':white_check_mark: **Zweryfikowano automatycznie** (obecność na starym serwerze)')
                embed = discord.Embed(description=text, color=discord.Color.green())
                await self.bot.get_channel(VERIFICATION_CHANNEL).send(embed=embed)
                await user.add_roles(interaction.guild.get_role(VERIFIED_ROLES[1]))
                try:
                    await user.edit(nick=old_member.nick)
                except discord.Forbidden:
                    pass
                return

        modal = GraduateVerificationModal()
        await interaction.response.send_modal(modal)
        await modal.wait()
        name, year, clss, teacher = list(map(lambda _: _.value, modal.children))
        if modal.children[0].value is None:
            return
        clss = clss.upper()

        text = f':mortar_board: **Absolwent - {user.mention}**\n' \
               f'Imię: `{name}`\n' \
               f'Klasa: `{clss}`\n' \
               f'Rok ukończenia: `{year}`\n' \
               f'Wychowawca: `{teacher}`'
        embed = discord.Embed(description=text, color=discord.Color.yellow())

        logger.info(f"Absolwent: {user.display_name}, Imię: {name}, Klasa: {clss}, Rok ukończenia: {year}, Wychowawca: "
                    f"{teacher}")

        view = discord.ui.View(timeout=None)
        view.add_item(ApproveButton(self.bot, user.id, 1))
        view.add_item(DenyButton(self.bot, user.id, 1))

        try:
            await user.edit(nick=name)
        except discord.Forbidden:
            pass
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
            text = (f':teacher: **Nauczyciel - {user.mention}**\n\n'
                    f':white_check_mark: **Zweryfikowano automatycznie** (lista ID)')
            embed = discord.Embed(description=text, color=discord.Color.green())
            await guild.get_channel(VERIFICATION_CHANNEL).send(embed=embed)
            return

        old_guild = self.bot.get_guild(OLD_GUILD)
        old_member = old_guild.get_member(user.id)
        if old_member is not None:
            if old_guild.get_role(OLD_VERIFIED_ROLES[2]) in old_member.roles:
                await interaction.response.send_message(
                    ":white_check_mark: **Weryfikacja przebiegła pomyślnie!**", ephemeral=True
                )
                logger.info(f"Nauczyciel: {user.display_name} zweryfikowany przez obecność na starym serwerze")
                text = (f':teacher: **Nauczyciel - {user.mention}**\n\n'
                        f':white_check_mark: **Zweryfikowano automatycznie** (obecność na starym serwerze)')
                embed = discord.Embed(description=text, color=discord.Color.green())
                await self.bot.get_channel(VERIFICATION_CHANNEL).send(embed=embed)
                await user.add_roles(interaction.guild.get_role(VERIFIED_ROLES[2]))
                try:
                    await user.edit(nick=old_member.nick)
                except discord.Forbidden:
                    pass
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
            text = (f":teacher: **Nauczyciel - {user.mention}**\n\n"
                    f"**Podane dane:**\n"
                    f"Imię i nazwisko: `{name}`\n"
                    f"Podany klucz: `{key}`\n\n"
                    f"Data utworzenia konta: <t:{int(user.created_at.timestamp())}:F>\n"
                    f"Data dołączenia do serwera: <t:{int(user.joined_at.timestamp())}:F>\n\n"
                    f":x: **Odrzucono automatycznie** (błędny klucz)")

            embed = discord.Embed(description=text, color=discord.Color.red())
            await self.bot.get_channel(VERIFICATION_CHANNEL).send(embed=embed)
            return

        try:
            await user.edit(nick=name)
        except discord.Forbidden:
            pass
        logger.info(f"Nauczyciel: {user.display_name} zweryfikowany przy pomocy klucza")
        await user.add_roles(guild.get_role(VERIFIED_ROLES[2]))
        text = (f':teacher: **Nauczyciel - {user.mention}**\n\n'
                f':white_check_mark: **Zweryfikowano automatycznie** (klucz weryfikacyjny)')
        embed = discord.Embed(description=text, color=discord.Color.green())
        await guild.get_channel(VERIFICATION_CHANNEL).send(embed=embed)
