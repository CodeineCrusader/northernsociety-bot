import discord

from embed_generator import embed_generator


class input_modal(discord.ui.Modal, title="Input Details Below"):
    modal = discord.ui.TextInput(
        label="Details", placeholder="Input Details Here.", max_length=2000, style=discord.TextStyle.long
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="*Your Submitted Details Have Been Received!*", ephemeral=True)


class ban_input_other(discord.ui.View):
    def __init__(self, user_id, data, other=False):
        super().__init__(timeout=600)
        self.value = None
        self.other = other
        self.user_id = user_id
        self.reason = None
        self.testimony = None
        self.data = data

    @discord.ui.button(label="Add Reason to Ban", style=discord.ButtonStyle.danger)
    async def input_reason(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            modal = input_modal()
            await interaction.response.send_modal(modal)
            await modal.wait()
            self.reason = modal
            self.data['Reason'] = modal.modal.value
            embed_gen = embed_generator(title="! User Ban Finalization !",
                                        description=f"**DO NOT DISMISS THIS MESSAGE**\nTo finalize the ban, please input the following information with the buttons below.\n\n1. Ban Reason - Reasoning for ban.\n2. Testimony - Description of the situation.",
                                        color=0xb80a0a, fields=self.data)
            embed = embed_gen.build()
            await interaction.edit_original_response(embed=embed)
        else:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await interaction.followup.send(content=f"You cannot respond to this prompt!", ephemeral=True)

    @discord.ui.button(label="Add Testimony to Ban", style=discord.ButtonStyle.danger)
    async def input_testimony(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            modal = input_modal()
            await interaction.response.send_modal(modal)
            await modal.wait()
            self.testimony = modal
            self.data['Testimony'] = modal.modal.value
            embed_gen = embed_generator(title="! User Ban Finalization !",
                                        description=f"**DO NOT DISMISS THIS MESSAGE**\nTo finalize the ban, please input the following information with the buttons below.\n\n1. Ban Reason - Reasoning for ban.\n2. Testimony - Description of the situation.",
                                        color=0xb80a0a, fields=self.data)
            embed = embed_gen.build()
            await interaction.edit_original_response(embed=embed)
        else:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await interaction.followup.send(content=f"*You cannot respond to this prompt!*", ephemeral=True)

    @discord.ui.button(label="Finalize Ban", emoji="✅", style=discord.ButtonStyle.success, row=3)
    async def finalize_ban(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True, thinking=True)
        if interaction.user.id == self.user_id:
            try:
                if self.reason.modal.value and self.testimony.modal.value:
                    await interaction.followup.send(content=f"*Ban Reasoning and Testimony Submitted!*")
                    self.stop()
            except AttributeError:
                await interaction.followup.send(content=f"*Please fill out both the testimony and the reasoning!*")
        else:
            return await interaction.followup.send(content=f"*You cannot respond to this prompt!*", ephemeral=True)
