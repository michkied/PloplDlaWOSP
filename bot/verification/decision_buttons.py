from ..config import *

from logzero import logger, logfile
import pathlib

path = str(pathlib.Path(__file__).parent.absolute())


class ApproveButton(discord.ui.Button):
    def __init__(self, bot, user_id, user_type):
        self.bot = bot
        self.user_id = int(user_id)
        self.guild = bot.get_guild(server_id)
        self.user_type = user_type

        super().__init__(label="Zatwierdź", style=discord.enums.ButtonStyle.green, custom_id=f'{user_id}_approve')

    async def callback(self, interaction: discord.Interaction):
        if self.guild.get_role(mod_role_id) not in interaction.user.roles:
            await interaction.response.send_message(':x: **Nie masz uprawnień by weryfikować użytkowników!**', ephemeral=True)
            logger.warning("Nie masz uprawnień by weryfikować użytkowników (nie mam jak sprawdzić kim jesteś)")
            return

        user = self.guild.get_member(self.user_id)
        await user.add_roles(self.guild.get_role(verified_roles[self.user_type]))
        await user.remove_roles(self.guild.get_role(unverified_roles[self.user_type]))

        description = f'{interaction.message.embeds[0].description}\n\n:white_check_mark: **Zweryfikowane przez {interaction.user.mention}** <t:{int(time.time())}>'
        logger.info(f"Zatwierdził: {interaction.user.display_name}")

        embed = discord.Embed(description=description, color=discord.Color.green())
        await interaction.message.edit(embed=embed, view=discord.ui.View())

        try:
            await user.send(':white_check_mark: **Twoje konto zostało zweryfikowane pomyślnie!**\nDziękujemy za weryfikację i zapraszamy do zadawania pytań.')
        except discord.Forbidden:
            pass


class DenyButton(discord.ui.Button):
    def __init__(self, bot, user_id, user_type):
        self.bot = bot
        self.user_id = user_id
        self.guild = bot.get_guild(server_id)
        self.user_type = user_type

        super().__init__(label="Odrzuć", style=discord.enums.ButtonStyle.red, custom_id=f'{user_id}_deny')

    async def callback(self, interaction: discord.Interaction):
        if self.guild.get_role(mod_role_id) not in interaction.user.roles:
            await interaction.response.send_message(':x: **Nie masz uprawnień by weryfikować użytkowników!**', ephemeral=True)
            logger.warning("Nie masz uprawnień by weryfikować użytkowników (nie mam jak sprawdzić kim jesteś)")
            return

        user = self.guild.get_member(self.user_id)
        await user.remove_roles(self.guild.get_role(unverified_roles[self.user_type]))

        description = f'{interaction.message.embeds[0].description}\n\n:x: **Odrzucone przez {interaction.user.mention}** <t:{int(time.time())}>'
        logger.info(f"Odrzucił: {interaction.user.display_name}")

        embed = discord.Embed(description=description, color=discord.Color.red())
        await interaction.message.edit(embed=embed, view=discord.ui.View())

        try:
            await user.send(':x: **Twój wniosek o weryfikację został odrzucony!**')
            await user.edit(nick=user.name)
        except discord.Forbidden:
            pass
