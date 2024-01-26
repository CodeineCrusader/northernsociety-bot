import io
import logging
import time

import chat_exporter
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button
from embed_generator import embed_generator
from interactions import RoleDropdownSelect, UserDropdownSelect

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(filename)s | %(levelname)s | %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
logger = logging.getLogger(__name__)

stream_h = logging.StreamHandler()
file_h = logging.FileHandler(f"logs/{time.strftime('%m-%d-%Y %H %M %S', time.localtime())}.log")

stream_h.setLevel(logging.WARNING)
file_h.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s | %(filename)s | %(levelname)s | %(message)s', '%m/%d/%Y %H:%M:%S')
stream_h.setFormatter(formatter)
file_h.setFormatter(formatter)

logger.addHandler(stream_h)
logger.addHandler(file_h)

staff_roles = [1158576945144004668, 1158576946914005082, 1158576945857048656, 1158576944061878273, 1158873454926372926, 1164618710376525834, 1158873235182600233, 1158576943663427654]


class ticket_closed(discord.ui.View):
    def __init__(self, user_id, original_opener):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.original_opener = original_opener
    @discord.ui.button(label="Delete", style=discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_roles = [role.id for role in interaction.user.roles]
        for role in user_roles:
            if role in staff_roles:
                staff = True
        if not staff:
            return await interaction.response.send_message("You cannot use this button!", ephemeral=True)
        channel = interaction.guild.get_channel(1159578058597085194)
        await interaction.response.send_message("*Ticket Deleted!*", ephemeral=True)
        transcript = await chat_exporter.export(interaction.channel, limit=None, tz_info='UTC')
        transcript_file = discord.File(io.BytesIO(transcript.encode()), filename=f"{interaction.channel.name}_transcript.html")
        await channel.send(file=transcript_file)
        await interaction.channel.delete()
        self.stop()


    @discord.ui.button(label="Reopen", style=discord.ButtonStyle.green)
    async def reopen(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_roles = [role.id for role in interaction.user.roles]
        for role in user_roles:
            if role in staff_roles:
                staff = True
        if not staff:
            return await interaction.response.send_message("You cannot use this button!", ephemeral=True)
        await interaction.response.send_message("*Ticket Reopened!*", ephemeral=True)
        await interaction.channel.set_permissions(interaction.guild.get_member(self.original_opener), view_channel=True, send_messages=True, read_message_history=True, read_messages=True)
        view = ticket_view(self.original_opener)
        await interaction.channel.send(content=f"*Ticket Reopened by {interaction.user.mention}!*", view=view)
        self.stop()


class ticket_close(discord.ui.View):
    def __init__(self, user_id, original_opener):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.original_opener = original_opener
        self.value = None
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green, custom_id="confirm")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("You cannot use this button!", ephemeral=True)
        await interaction.response.send_message("*Ticket Closed!*", ephemeral=True)
        await interaction.channel.edit(sync_permissions=True)
        if "preport" in interaction.channel.name:
            await interaction.channel.set_permissions(interaction.guild.get_role(1158576946914005082), view_channel=True, send_messages=True, read_message_history=True, read_messages=True)
            await interaction.channel.set_permissions(interaction.guild.get_role(1158576945857048656), view_channel=True, send_messages=True, read_message_history=True, read_messages=True)
        view = ticket_closed(interaction.user.id, self.original_opener)
        await interaction.channel.send(content=f"*Ticket Closed by {interaction.user.mention}*", view=view)
        self.value = True
        self.stop()
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, custom_id="cancel")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("You cannot use this button!", ephemeral=True)
        await interaction.response.send_message("*Ticket Close Cancelled!*", ephemeral=True)
        self.value = False
        self.stop()


class ticket_view(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.add_item(UserDropdownSelect(placeholder="Add Users", max_values=10, custom_id="user_ticket_add"))
        self.add_item(RoleDropdownSelect(placeholder="Add Roles", max_values=10, custom_id="role_ticket_add"))
    @discord.ui.button(label="Close", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction,  button: discord.ui.Button):
        user_roles = [role.id for role in interaction.user.roles]
        for role in user_roles:
            if role in staff_roles:
                break
        else:
            return await interaction.response.send_message("You cannot use this button!", ephemeral=True)
        if interaction.user.id == self.user_id:
            while True:
                view = ticket_close(interaction.user.id, self.user_id)
                await interaction.response.send_message("*Are you sure you want to close this ticket?*", view=view, ephemeral=True)
                await view.wait()
                if view.value:
                    break
        else:
            return await interaction.response.send_message("You cannot use this button!", ephemeral=True)
        self.stop()


class tickets(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    ticket = app_commands.Group(name="ticket", description="Commands in Relation to the Ticket Module.")

    @ticket.command(name="support", description="Create Support Ticket Embed")
    @app_commands.checks.has_permissions(administrator=True)
    async def support(self, interaction: discord.Interaction):
        if not interaction.guild_id == 1158271879556104204:
            return interaction.response.send_message("You need to be in the main server to execute this command!", ephemeral=True)
        channel = self.client.get_channel(1159362455785443348)
        fields = {"Server Support": "Support Tickets used to collect roles, ask questions, as well as for redeeming items in the community. Any inquiries that are not reports on staff or players will be answered in here.",
                  "Player Report": "Player Report Tickets are used for violations of the community guidelines. This may be for a member breaking a rule or a member of emergency services that is in violation of law or department guidelines or standards. These tickets are reviewed by community moderation if a player is reported and public safety if the player was in violation of DPS guidelines.",
                  "Staff Report": "Staff Report Tickets are used when a member of our community staff are in violation of community guidelines, staff guidelines, corruption, or abuse of authority. These tickets are reviewed by management directly."
        }
        generator = embed_generator(
            title="North Society Ticket Booth",
            description="Welcome to the Support Area! We ask that you remain patient while our team gets to your ticket. We ask that you create only one ticket per instance. We also ask that you use the correct ticket for the instance you need assistance with.",
            color=0xC08C38,
            image_url="https://media.discordapp.net/attachments/1161404493016076328/1184080280177344553/Embed_Bottom.png?ex=65a65b31&is=6593e631&hm=0231e99ece59d8580afa4a08b30b81a60e9eab8bb37faff69f4bab6ac2f71482&=&format=webp&quality=lossless&width=960&height=24",
            fields=fields,
        )
        mainEmbed = generator.build()
        imageEmbed = discord.Embed(color=0xC08C38)
        imageEmbed.set_image(url="https://cdn.discordapp.com/attachments/1161404493016076328/1184079382617268234/NSRP_Embed.png?ex=65a65a5b&is=6593e55b&hm=27f8114862a965498ee98ec2216956b55952677a4472dd0c34b765170aa6aacf&")
        view = discord.ui.View()

        ss_open = Button(style=discord.ButtonStyle.green, label="Server Support", custom_id="ss", emoji="📩")
        pr_open = Button(style=discord.ButtonStyle.danger, label="Player Report", custom_id="pr", emoji="⚔")
        sr_open = Button(style=discord.ButtonStyle.blurple, label="Staff Report", custom_id="sr", emoji="🛡️")

        view.add_item(ss_open)
        view.add_item(pr_open)
        view.add_item(sr_open)

        await channel.send(embeds=[imageEmbed, mainEmbed], view=view)
        await interaction.response.send_message("Support Embed Created!", ephemeral=True)


    @ticket.command(name="add", description="Add User to Current Ticket")
    @app_commands.checks.has_any_role(1158576945144004668, 1158576946914005082, 1158576945857048656, 1158576944061878273, 1158873454926372926, 1164618710376525834, 1158873235182600233, 1158576943663427654)
    async def add(self, interaction: discord.Interaction, user: discord.Member):
        if interaction.channel.category.id not in [1193318391277158460, 1193318818542522398]:
            return await interaction.response.send_message("*You need to be in a ticket to execute this command!*", ephemeral=True)
        elif interaction.channel.category_id == 1193318818542522398 and "sreport" in interaction.channel.name:
            user_roles = [role.id for role in interaction.user.roles]
            for id in [1158576944061878273, 1158873454926372926, 1164618710376525834, 1158873235182600233, 1158576943663427654]:
                if id in user_roles:
                    break
            else:
                return await interaction.response.send_message(f"*You cannot add users inside staff report tickets! (Asst. Manager+)*", ephemeral=True)
        try:
            await interaction.channel.set_permissions(user, view_channel=True, send_messages=True, read_message_history=True, read_messages=True)
        except Exception:
            return await interaction.response.send_message(f"*An error occured while adding {user.mention} to {interaction.channel.mention}!*", ephemeral=True)
        await interaction.response.send_message(f"*Successfully added {user.mention} to {interaction.channel.mention}!*", ephemeral=True)


    @ticket.command(name="remove", description="Remove User from Current Ticket")
    @app_commands.checks.has_any_role(1158576945144004668, 1158576946914005082, 1158576945857048656, 1158576944061878273, 1158873454926372926, 1164618710376525834, 1158873235182600233, 1158576943663427654)
    async def remove(self, interaction: discord.Interaction, user: discord.Member):
        if interaction.channel.category.id not in [1193318391277158460, 1193318818542522398]:
            return await interaction.response.send_message("*You need to be in a ticket to execute this command!*", ephemeral=True)
        elif interaction.channel.category_id == 1193318818542522398 and "sreport" in interaction.channel.name:
            user_roles = [role.id for role in interaction.user.roles]
            for id in [1158576944061878273, 1158873454926372926, 1164618710376525834, 1158873235182600233, 1158576943663427654]:
                if id in user_roles:
                    break
            else:
                return await interaction.response.send_message(f"*You cannot remove users from staff report tickets! (Asst. Manager+)*", ephemeral=True)
        try:
            await interaction.channel.set_permissions(user, view_channel=False, send_messages=False, read_message_history=False, read_messages=False)
        except Exception:
            return await interaction.response.send_message(f"*An error occured while removing {user.mention} from {interaction.channel.mention}!*", ephemeral=True)
        await interaction.response.send_message(f"*Successfully removed {user.mention} from {interaction.channel.mention}!*", ephemeral=True)


    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        try:
            buttonPressed = interaction.data['custom_id']
            guild = self.client.get_guild(1158271879556104204)
            support_category = discord.utils.get(guild.categories, name="Server Support Tickets")
            report_category = discord.utils.get(guild.categories, name="Server Report Tickets")

            if "ss" in buttonPressed:
                channel = await guild.create_text_channel(f"{interaction.user.name}-support", category=support_category)
                generator = embed_generator(
                    title="North Society Support",
                    description="PLACEHOLDER TEXT",
                    color=0xC08C38,
                    fields={},
                    author="PLACEHOLDER",
                    author_icon_url="https://cdn.discordapp.com/icons/1158271879556104204/129ad674a4c2a9eea1df068459e5ba00.webp?size=1024&format=webp&width=0&height=204",
                    footer="PLACEHOLDER",
                    footer_icon_url="https://cdn.discordapp.com/icons/1158271879556104204/129ad674a4c2a9eea1df068459e5ba00.webp?size=1024&format=webp&width=0&height=204",
                )
                embed = generator.build()
                view = ticket_view(interaction.user.id)
                await channel.set_permissions(interaction.user, view_channel=True, send_messages=True, read_message_history=True, read_messages=True)
                await interaction.response.send_message(f"*Your ticket has been created! Please navigate to <#{channel.id}> to continue your support request.*", ephemeral=True)
                await channel.send(content=f"{interaction.user.mention} <@&1158576945144004668>", embed=embed, view=view)
            elif "pr" in buttonPressed:
                channel = await guild.create_text_channel(f"{interaction.user.name}-preport", category=report_category)
                generator = embed_generator(
                    title="North Society Support",
                    description="PLACEHOLDER TEXT",
                    color=0xC08C38,
                    fields={},
                    author="PLACEHOLDER",
                    author_icon_url="https://cdn.discordapp.com/icons/1158271879556104204/129ad674a4c2a9eea1df068459e5ba00.webp?size=1024&format=webp&width=0&height=204",
                    footer="PLACEHOLDER",
                    footer_icon_url="https://cdn.discordapp.com/icons/1158271879556104204/129ad674a4c2a9eea1df068459e5ba00.webp?size=1024&format=webp&width=0&height=204",
                )
                embed = generator.build()
                view = ticket_view(interaction.user.id)
                await channel.set_permissions(guild.get_role(1158576946914005082), view_channel=True, send_messages=True, read_message_history=True, read_messages=True)
                await channel.set_permissions(guild.get_role(1158576945857048656), view_channel=True, send_messages=True, read_message_history=True, read_messages=True)
                await channel.set_permissions(interaction.user, view_channel=True, send_messages=True, read_message_history=True, read_messages=True)
                await interaction.response.send_message(f"*Your ticket has been created! Please navigate to <#{channel.id}> to continue your report.*", ephemeral=True)
                await channel.send(content=f"{interaction.user.mention} <@&1158576946914005082> <@&1158576945857048656>", embed=embed, view=view)
            elif "sr" in buttonPressed:
                original_opener = interaction.user
                channel = await guild.create_text_channel(f"{interaction.user.name}-sreport", category=report_category)
                generator = embed_generator(
                    title="North Society Support",
                    description="PLACEHOLDER TEXT",
                    color=0xC08C38,
                    fields={},
                    author="PLACEHOLDER",
                    author_icon_url="https://cdn.discordapp.com/icons/1158271879556104204/129ad674a4c2a9eea1df068459e5ba00.webp?size=1024&format=webp&width=0&height=204",
                    footer="PLACEHOLDER",
                    footer_icon_url="https://cdn.discordapp.com/icons/1158271879556104204/129ad674a4c2a9eea1df068459e5ba00.webp?size=1024&format=webp&width=0&height=204",
                )
                embed = generator.build()
                view = ticket_view(interaction.user.id)
                await channel.set_permissions(interaction.user, view_channel=True, send_messages=True, read_message_history=True, read_messages=True)
                await interaction.response.send_message(f"*Your ticket has been created! Please navigate to <#{channel.id}> to continue your report.*", ephemeral=True)
                await channel.send(content=f"{interaction.user.mention} <@&1158576944061878273> <@&1158873454926372926>", embed=embed, view=view)
        except AttributeError:
            pass
        except KeyError:
            pass


async def setup(client: commands.Bot):
    await client.add_cog(tickets(client))
    logger.info(f"cogs.tickets.py Successfully Loaded!")