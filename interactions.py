from typing import Any, Optional

import discord
from discord.interactions import Interaction
from discord.utils import MISSING

from embed_generator import embed_generator

staff_roles = [1158576945144004668, 1158576946914005082, 1158576945857048656, 1158576944061878273, 1158873454926372926, 1164618710376525834, 1158873235182600233, 1158576943663427654]

class input_modal(discord.ui.Modal, title="Input Details Below"):
    def __init__(self, *, submit_message: str) -> None:
        super().__init__()
        self.submit_message = submit_message
    modal = discord.ui.TextInput(
        label="Details", placeholder="Input Details Here.", max_length=2000, style=discord.TextStyle.long
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(content=self.submit_message, ephemeral=True)


class ban_reason_modal(discord.ui.Modal, title="Input Details Below"):
    def __init__(self, *, submit_message: str) -> None:
        super().__init__()
        self.submit_message = submit_message
    modal = discord.ui.TextInput(
        label="Details", placeholder="Input Details Here.", max_length=450, style=discord.TextStyle.long
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(content=self.submit_message, ephemeral=True)


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
            modal = ban_reason_modal(submit_message="*Ban Reason Submitted.*")
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
            modal = input_modal(submit_message="Ban Testimony Submitted.")
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


class UserDropdownSelect(discord.ui.UserSelect):
    def __init__(self, *, custom_id: str, placeholder: str | None = None, min_values: int = 1, max_values: int = 1, disabled: bool = False, row: int | None = None) -> None:
        super().__init__(placeholder=placeholder, min_values=min_values, max_values=max_values, disabled=disabled, row=row)
        self.custom_id = custom_id
        
    async def callback(self, interaction: discord.Interaction) -> Any:
        self.value = [item for item in self.values]
        user_roles = [role.id for role in interaction.user.roles]
        for role in user_roles:
            if role in staff_roles:
                staff = True
        if not staff:
            return await interaction.response.send_message("You cannot use this dropdown!", ephemeral=True)

        match self.custom_id:
            case "user_ticket_add":
                for item in self.value:
                    await interaction.channel.set_permissions(item, view_channel=True, send_messages=True, read_message_history=True, read_messages=True)
                    await interaction.channel.send(content=f"*Successfully Added {item.mention} to {interaction.channel.mention}!*")
                else:
                    await interaction.response.send_message(content="*Channel Permissions Updated!*", ephemeral=True)


class RoleDropdownSelect(discord.ui.RoleSelect):
    def __init__(self, *, custom_id: str, placeholder: str | None = None, min_values: int = 1, max_values: int = 1, disabled: bool = False, row: int | None = None) -> None:
        super().__init__(placeholder=placeholder, min_values=min_values, max_values=max_values, disabled=disabled, row=row)
        self.value = None
        self.custom_id = custom_id
        
    async def callback(self, interaction: discord.Interaction) -> Any:
        self.value = [item for item in self.values]
        user_roles = [role.id for role in interaction.user.roles]
        for role in user_roles:
            if role in staff_roles:
                staff = True
        if not staff:
            return await interaction.response.send_message("You cannot use this dropdown!", ephemeral=True)
        
        match self.custom_id:
            case "role_ticket_add":
                for item in self.value:
                    await interaction.channel.set_permissions(item, view_channel=True, send_messages=True, read_message_history=True, read_messages=True)
                    await interaction.channel.send(content=f"*Successfully Added {item.mention} to {interaction.channel.mention}!*")
                else:
                    await interaction.response.send_message(content="*Channel Permissions Updated!*", ephemeral=True)
