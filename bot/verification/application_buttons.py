from .decision_buttons import *
import discord.ui as ui


class VerifyStudentButton(discord.ui.Button):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(label="🎒 Uczeń", style=discord.enums.ButtonStyle.blurple, custom_id="0")

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user

        if unverified_roles[0] in (role.id for role in user.roles) or unverified_roles[1] in (role.id for role in user.roles):
            await interaction.response.send_message(
                ":x: **Cierpliwości!**\nTwoje zgłoszenie już do nas dotarło i jest w trakcie weryfikacji.",
                ephemeral=True
            )
            return

        modal = ui.Modal(
            title="Weryfikacja konta ucznia",
            timeout=3600
        )
        modal.add_item(ui.InputText(
                style=discord.InputTextStyle.short,
                label="Jak masz na imię i nazwisko?")
        )
        modal.add_item(ui.InputText(
                style=discord.InputTextStyle.short,
                label="Do której klasy chodzisz?",
                max_length=2,
                min_length=2)
        )

        async def callback(modal_interaction):
            text = f'**To wszystko!**\n' \
                   f'Wielkie dzięki za wypełnienie formularza. Właśnie został on przesłany do naszych moderatorów, ' \
                   f'którzy postarają się jak najszybciej sprawdzić Twoje dane.'
            await modal_interaction.response.send_message(text, ephemeral=True)

        modal.callback = callback
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


class VerifyGraduateButton(discord.ui.Button):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(label="🎓 Absolwent", style=discord.enums.ButtonStyle.blurple, custom_id="2")

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user

        if unverified_roles[0] in (role.id for role in user.roles) or unverified_roles[1] in (role.id for role in user.roles):
            await interaction.response.send_message(":x: **Cierpliwości!**\nTwoje zgłoszenie już do nas dotarło i jest w trakcie weryfikacji.", ephemeral=True)
            return

        modal = ui.Modal(
            title="Weryfikacja konta absolwenta",
            timeout=3600
        )
        modal.add_item(ui.InputText(
            style=discord.InputTextStyle.short,
            label="Jak masz na imię i nazwisko?")
        )
        modal.add_item(ui.InputText(
            style=discord.InputTextStyle.short,
            label="W którym roku skończyłaś/eś naukę?",
            max_length=4,
            min_length=4)
        )
        modal.add_item(ui.InputText(
            style=discord.InputTextStyle.short,
            label="Do której klasy chodziłaś/eś?",
            placeholder="(tylko litery)",
            max_length=2,
            min_length=1)
        )
        modal.add_item(ui.InputText(
            style=discord.InputTextStyle.short,
            label="Kto był twoim wychowawcą?")
        )

        async def callback(modal_interaction):
            text = f'**To wszystko!**\n' \
                   f'Wielkie dzięki za wypełnienie formularza. Właśnie został on przesłany do naszych moderatorów, ' \
                   f'którzy postarają się jak najszybciej sprawdzić Twoje dane.'
            await modal_interaction.response.send_message(text, ephemeral=True)

        modal.callback = callback
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


class VerifyTeacherButton(discord.ui.Button):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(label="🧑‍🏫 Nauczyciel", style=discord.enums.ButtonStyle.blurple, custom_id="1")

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild

        if user.id in teachers:
            logger.info(f"Nauczyciel: {user.display_name} znaleziony na liście ID")
            await user.add_roles(guild.get_role(verified_roles[2]))
            await interaction.response.send_message(":white_check_mark: **Weryfikacja przebiegła pomyślnie!**", ephemeral=True)
            await guild.get_channel(applications_channel).send(f':white_check_mark::teacher: **Użytkownik {user.mention} zweryfikował się jako nauczyciel**')
            return

        modal = ui.Modal(
            title="Weryfikacja konta nauczyciela",
            timeout=3600
        )
        modal.add_item(ui.InputText(
            style=discord.InputTextStyle.short,
            label="Jak masz na imię i nazwisko?")
        )

        async def callback(modal_interaction):
            text = f'**To wszystko!**\n' \
                   f'Formularz został przesłany do naszych moderatorów, ' \
                   f'którzy postarają się jak najszybciej sprawdzić Twoje dane.'
            await modal_interaction.response.send_message(text, ephemeral=True)

        modal.callback = callback
        await interaction.response.send_modal(modal)
        await modal.wait()
        name = modal.children[0].value

        await user.edit(nick=name)

        text = f"**Nauczyciel - {user.mention}**\n" \
               f"Imię: {name}\n\n" \
               f"Data utworzenia konta: <t:{int(user.created_at.timestamp())}:F>\n" \
               f"Data dołączenia do serwera: <t:{int(user.joined_at.timestamp())}:F>"

        embed = discord.Embed(description=text, color=discord.Color.blurple())

        logger.warning(f"Nauczyciel: {user.display_name} - {name}")

        view = discord.ui.View(timeout=None)
        view.add_item(ApproveButton(self.bot, user.id, 2))
        view.add_item(DenyButton(self.bot, user.id, 2))

        await self.bot.get_channel(applications_channel).send(embed=embed, view=view)
        await user.add_roles(interaction.guild.get_role(unverified_roles[2]))
