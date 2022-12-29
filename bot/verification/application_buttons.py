from .decision_buttons import *


async def wait_for_message(bot, check, followup):
    try:
        return await bot.wait_for('message', check=check, timeout=3600)
    except asyncio.TimeoutError:
        await followup.send(':x: **Czas na odpowiedź minął!**\nWciśnij przycisk wyboru jeszcze raz', ephemeral=True)
        return


class VerifyStudentButton(discord.ui.Button):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(label="🎒 Uczeń", style=discord.enums.ButtonStyle.blurple, custom_id="0")

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user

        if unverified_roles[0] in (role.id for role in user.roles) or unverified_roles[1] in (role.id for role in user.roles):
            await interaction.response.send_message(":x: **Cierpliwości!**\nTwoje zgłoszenie już do nas dotarło i jest w trakcie weryfikacji.", ephemeral=True)
            return

        def check(m):
            return m.author.id == user.id and m.channel == interaction.channel

        await interaction.response.send_message("**Super!**\nJeszcze jedno - do weryfikacji będziemy potrzebować twojego **imienia**, **nazwiska** oraz **klasy**.\n\n**Podaj te dane odpisując na tym kanale**", ephemeral=True)
        followup = interaction.followup

        message = await wait_for_message(self.bot, check, followup)
        if not message:
            return
        data = message.content
        logger.info(f"Uczeń: {user.display_name} Podany nick: {str(data)}")

        await message.author.edit(nick=message.content)
        # await message.delete()

        text = f'**To wszystko!**\n' \
               f'Wielkie dzięki za wypełnienie formularza. Właśnie został on przesłany do naszych moderatorów, ' \
               f'którzy postarają się jak najszybciej sprawdzić Twoje dane.'
        await followup.send(text, ephemeral=True)

        if user.id not in users_data:
            other_guilds = ':warning: **Użytkownika nie ma na żadnym serwerze klasowym**'
        else:
            other_guilds = '`Na innych serwerach:`\n'
            for guild in users_data[user.id]:
                other_guilds += f'{guild["guild"]}  -  {guild["nick"]}\n'

        text = f'**Uczeń - {user.mention}**\n' \
               f'`Podane dane` - {data}\n\n' \
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

        def check(m):
            return m.author.id == user.id and m.channel == interaction.channel

        await interaction.response.send_message("**Super!**\nPoprosimy Cię teraz o odpowiedź na kilka krótkich pytań.\n\n*(1/4)* **Jak masz na imię i nazwisko?**", ephemeral=True)
        followup = interaction.followup

        message = await wait_for_message(self.bot, check, followup)
        if not message:
            return
        name = message.content

        await message.author.edit(nick=message.content)
        # await message.delete()
        await followup.send(f':wave: **Miło cię widzieć, {name}!**\n\n*(2/4)* **Do której klasy chodziłaś/chodziłeś?**', ephemeral=True)

        message = await wait_for_message(self.bot, check, followup)
        if not message:
            return
        clss = message.content
        # await message.delete()
        await followup.send(f'**Klasa {clss}, zapisane!**\n\n*(3/4)* **W którym roku skończyłaś/skończyłeś naukę?**', ephemeral=True)

        message = await wait_for_message(self.bot, check, followup)
        if not message:
            return
        year = message.content
        # await message.delete()
        await followup.send(f'**Rocznik {year}, zapisane**\n\n*(4/4)* **Kto był twoim wychowawcą?**', ephemeral=True)

        message = await wait_for_message(self.bot, check, followup)
        if not message:
            return
        teacher = message.content
        # await message.delete()
        text = f'**Wychowawca - {teacher}**\n\n' \
               f'**To tyle!**\n' \
               f'Wielkie dzięki za wypełnienie formularza. Właśnie został on przesłany do naszych moderatorów, ' \
               f'którzy postarają się jak najszybciej sprawdzić Twoje dane.'
        await followup.send(text, ephemeral=True)

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

        def check(m):
            return m.author.id == user.id and m.channel == interaction.channel

        user = interaction.user
        guild = interaction.guild

        if user.id not in teachers:
            await interaction.response.send_message(":x: **Nie jesteś zarejestrowana/y jako nauczyciel! "
                                                    "Jak się nazywasz?**", ephemeral=True)
            followup = interaction.followup

            message = await wait_for_message(self.bot, check, followup)
            if not message:
                return

            name = message.content

            await message.author.edit(nick=message.content)
            # await message.delete()
            await followup.send(
                f':wave: {name} - zapisałem! Zaczekaj chwilę, nasi uczniowie sprawdzą czy na pewno jesteś nauczycielem',
                ephemeral=True)

            text = f"**Nauczyciel: {user.display_name}**\n" \
                   f"Nazywa się: {name}"

            embed = discord.Embed(description=text, color=discord.Color.blurple())

            logger.warning(f"Nauczyciel: {user.display_name} - {name}")

            view = discord.ui.View(timeout=None)
            view.add_item(ApproveButton(self.bot, user.id, 2))
            view.add_item(DenyButton(self.bot, user.id, 2))

            await self.bot.get_channel(applications_channel).send(embed=embed, view=view)
            await user.add_roles(interaction.guild.get_role(unverified_roles[2]))
        else:

            logger.info(f"Nauczyciel: {user.display_name} znaleziony w liście ID")

            await user.add_roles(guild.get_role(verified_roles[2]))
            await interaction.response.send_message(":white_check_mark: **Weryfikacja przebiegła pomyślnie!**", ephemeral=True)
            await guild.get_channel(applications_channel).send(f':white_check_mark::teacher: **Użytkownik {user.mention} zweryfikował się jako nauczyciel**')
