import discord.ui as ui
from ..config import *


class StudentVerificationModal(ui.Modal):
    def __init__(self, student_keys):
        super().__init__(
            title="Weryfikacja konta ucznia",
            timeout=3600
        )
        self.student_keys = student_keys

        self.add_item(ui.InputText(
                style=discord.InputTextStyle.short,
                label="Imię i nazwisko")
        )
        self.add_item(ui.InputText(
                style=discord.InputTextStyle.short,
                label="Klasa",
                max_length=2,
                min_length=2)
        )
        self.add_item(ui.InputText(
                style=discord.InputTextStyle.short,
                label="Klucz weryfikacyjny",
                placeholder="(otrzymany od przewodniczącego klasy)")
        )

    async def callback(self, interaction):
        name, clss, key = list(map(lambda _: _.value, self.children))
        key = key.upper()

        if key not in self.student_keys:
            await interaction.response.send_message(
                ':x: **Podany klucz weryfikacyjny jest niepoprawny!**', ephemeral=True
            )
            return

        if name.lower() != self.student_keys[key][0].lower() or clss.lower() != self.student_keys[key][1].lower():
            text = f'**Podane dane wymagają dodatkowej weryfikacji**\n' \
                f'Automatyczna weryfikacja Twojego konta nie powiodła się. Wypełniony przez Ciebie formularz ' \
                f'został przesłany do naszych moderatorów, którzy postarają się jak najszybciej sprawdzić Twoje dane.'
            await interaction.response.send_message(text, ephemeral=True)
            return

        await interaction.response.send_message(
            ":white_check_mark: **Weryfikacja przebiegła pomyślnie!**", ephemeral=True
        )


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

