import discord.ui as ui
from ..config import *


class StudentVerificationModal(ui.Modal):
    def __init__(self):
        super().__init__(
            title="Weryfikacja konta ucznia",
            timeout=3600
        )

        self.add_item(ui.InputText(
                style=discord.InputTextStyle.short,
                label="Jak masz na imię i nazwisko?")
        )
        self.add_item(ui.InputText(
                style=discord.InputTextStyle.short,
                label="Do której klasy chodzisz?",
                max_length=2,
                min_length=2)
        )

    async def callback(self, interaction):
        text = f'**To wszystko!**\n' \
               f'Wielkie dzięki za wypełnienie formularza. Właśnie został on przesłany do naszych moderatorów, ' \
               f'którzy postarają się jak najszybciej sprawdzić Twoje dane.'
        await interaction.response.send_message(text, ephemeral=True)


class GraduateVerificationModal(ui.Modal):
    def __init__(self):
        super().__init__(
            title="Weryfikacja konta absolwenta",
            timeout=3600
        )
        self.add_item(ui.InputText(
            style=discord.InputTextStyle.short,
            label="Jak masz na imię i nazwisko?")
        )
        self.add_item(ui.InputText(
            style=discord.InputTextStyle.short,
            label="W którym roku skończyłaś/eś naukę?",
            max_length=4,
            min_length=4)
        )
        self.add_item(ui.InputText(
            style=discord.InputTextStyle.short,
            label="Do której klasy chodziłaś/eś?",
            placeholder="(tylko litery)",
            max_length=2,
            min_length=1)
        )
        self.add_item(ui.InputText(
            style=discord.InputTextStyle.short,
            label="Kto był twoim wychowawcą?")
        )

    async def callback(self, interaction):
        text = f'**To wszystko!**\n' \
               f'Wielkie dzięki za wypełnienie formularza. Właśnie został on przesłany do naszych moderatorów, ' \
               f'którzy postarają się jak najszybciej sprawdzić Twoje dane.'
        await interaction.response.send_message(text, ephemeral=True)


class TeacherVerificationModal(ui.Modal):
    def __init__(self):
        super().__init__(
            title="Weryfikacja konta nauczyciela",
            timeout=3600
        )
        self.add_item(ui.InputText(
            style=discord.InputTextStyle.short,
            label="Imię i nazwisko")
        )
        self.add_item(ui.InputText(
            style=discord.InputTextStyle.short,
            label="Kod dostępu",
            placeholder="(przesłany na librusie)")
        )

    async def callback(self, interaction):
        text = ':white_check_mark: **Weryfikacja przebiegła pomyślnie!**'
        if self.children[1].value != TEACHER_KEY:
            text = ':x: **Podany kod dostępu jest niepoprawny!**'
        await interaction.response.send_message(text, ephemeral=True)

