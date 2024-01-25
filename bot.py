import logging
import os
import platform
import random
import time

import colorama
import discord
import jishaku
from discord import app_commands, ui
from discord.ext import commands, tasks
from discord.ui import Button, View
from discord.utils import get, setup_logging
from dotenv import dotenv_values

from embed_generator import embed_generator
from interactions import ban_input_other, input_modal

config = dotenv_values(".env")

colorama.init(autoreset=True)

dir_path = os.path.dirname(os.path.realpath(__file__))

if not os.path.exists(f'{dir_path}\\logs'):
    os.makedirs(f'{dir_path}\\logs')

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

match config["ENVIRONMENT"].upper():
    case "PRODUCTION":
        prefix = config["prefix_prod"]
    case "DEVELOPMENT":
        prefix = config["prefix_dev"]

@tasks.loop(minutes=1)
async def status():
    choices = [
        discord.Activity(type=discord.ActivityType.listening, name='Closely'),
    ]
    chosen = random.choice(choices)
    await client.change_presence(activity=chosen)


class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or(prefix), case_insensitive=True, intents=discord.Intents.all())
        self.cogs_list = ['jishaku', 'cogs.tickets']

    async def setup_hook(self):
        for ext in self.cogs_list:
            await self.load_extension(ext)

    async def on_ready(self):
        logger.info(f"Logging in as {self.user.name}")
        logger.info(f"Client ID: {self.user.id}")
        logger.info(f"Discord Version: {discord.__version__}")
        logger.info(f"Python Version: {platform.python_version()}")
        status.start()
        logger.info(f"Status Loop Started")

        channel = client.get_channel(1160811638463672390)
        await channel.send(f'{client.user.mention} is now online!')


client = Client()
client.remove_command("help")


@client.event
async def on_member_join(member):
    if member.guild.id == 1158271879556104204:
        await member.add_roles(get(member.guild.roles, name="Non-Whitelisted"))


@client.tree.command(name='purge', description="Purge [a] message(s) from a channel.")
@commands.has_permissions(manage_messages=True)
@app_commands.describe(limit="The count of message(s) you want deleted.")
@app_commands.rename(limit='count')
async def purge(interaction: discord.Interaction,limit: int):
    channel = client.get_channel(interaction.channel_id)
    if limit == 0:
        await interaction.response.send_message('You cannot purge 0 messages!', ephemeral=True)
        return
    try:
        if channel == interaction.user.dm_channel:
            user_id = interaction.user.id
            async for message in client.get_user(user_id).history(limit=limit):
                if message.author.id == client.user.id:
                    await message.delete()
            await interaction.response.send_message(f'Successfully purged `{limit}` message(s)!',ephemeral=True)
        elif channel in interaction.guild.channels:
            await channel.purge(limit=limit)
            await interaction.response.send_message(f'Successfully purged `{limit}` message(s) inside `{channel}`!', ephemeral=True)
    except Exception as e:
        if e == commands.CommandInvokeError:
            await interaction.response.send_message(f'Successfully purged `{limit}` message(s) inside `{channel}`!',
                                                    ephemeral=True)
        elif e == commands.MissingPermissions:
            await interaction.response.send_message('You do not have permission to use this command!', ephemeral=True)


@client.tree.command(name="ban")
@app_commands.describe(
    ban_user="Select the User You Wish to Ban.",
    ban_type="Select the Type of Ban.",
)
@app_commands.choices(
    ban_type=[
        app_commands.Choice(name="Soft Ban", value="1a"),  # Bans User from Server with an Immediate Unban, effective to delete user messages
        app_commands.Choice(name="Hard Ban", value="1b")  # Bans User from Server within Specified Time
    ]
)
@app_commands.rename(
    ban_user="user",
    ban_type="type",
)
@commands.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, ban_user: discord.User, ban_type: app_commands.Choice[str]):
    await interaction.response.defer(ephemeral=True, thinking=True)
    if interaction.user.id == ban_user.id:
        return await interaction.followup.send(content=f"*Please specify the user you wish to ban. You're unable to ban yourself from this guild!*")
    log_channel = client.get_channel(1159578058597085194)
    reason_testimony = {"Reason": "*Reason Has Yet to Be Provided*", "Testimony": "*Testimony Has Yet to Be Provided*"}
    embed_gen = embed_generator(title="! User Ban Finalization !",
                                description=f"**DO NOT DISMISS THIS MESSAGE**\nTo finalize the ban, please input the following information with the buttons below.\n\n1. Ban Reason - Reasoning for ban.\n2. Testimony - Description of the situation.",
                                color=0xb80a0a, fields=reason_testimony)
    embed = embed_gen.build()
    view = ban_input_other(user_id=interaction.user.id, other=True, data=reason_testimony)
    await interaction.followup.send(embed=embed, view=view)
    await view.wait()
    match ban_type.value:
        case "1a":
            # TODO: Create Soft Bans, Add and Remove Ban with Specified Reason and Testimony sent in Staff Channel
            ban_type_str = "Soft Ban"
            reason_str = f"{reason_testimony["Reason"]} (Soft Ban by {interaction.user.global_name})"
            await ban_user.create_dm()
            await ban_user.dm_channel.send(content=f"*You have been banned from `{interaction.guild.name}` for `{reason_testimony["Reason"]}`")
            await interaction.guild.ban(user=ban_user, reason=reason_str)
            await interaction.guild.unban(user=ban_user, reason=reason_str)
        case "1b":
            # TODO: Create Hard Ban, Ban User for Specified Time and Submit Testimony to Staff Channel
            ban_type_str = "Hard Ban"
            reason_str = f"{reason_testimony["Reason"]} (Hard Ban by {interaction.user.name})"
            await ban_user.create_dm()
            await ban_user.dm_channel.send(content=f"*You have been banned from `{interaction.guild.name}` for `{reason_testimony["Reason"]}`")
            await interaction.guild.ban(user=ban_user, reason=reason_str)
    embed = embed_generator(
                title="Ban Submitted", description=f"**PLACEHOLDER DESCRIPTION**\n\nBan Information:\nUser: {ban_user}\nType: {ban_type_str}\nModerator: {interaction.user}\n\n Reason: {reason_testimony['Reason']}\nTestimony: {reason_testimony['Testimony']}", color=0xC08C38, fields={},
            ).build()
    await log_channel.send(embed=embed)


@client.tree.command(name="unban")
@app_commands.describe(
    user_input="The User ID of the User You'd Like to Unban.",
    unban_reason="Reason for Unbanning this User.",
)
@app_commands.rename(
    user_input="user",
    unban_reason="reason",
)
@commands.has_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, user_input: str, unban_reason: str):
    # await interaction.response.defer(ephemeral=True, thinking=True)
    user_id = int(user_input)
    user_snowflake = await client.fetch_user(user_id)
    if not user_snowflake:
        return await interaction.followup.send(content=f"*Please specify the user you wish to unban. This needs to be a valid Discord User ID!*")
    if interaction.user.id == user_id:
        return await interaction.followup.send(content=f"*Please specify the user you wish to unban. You're unable to unban yourself from this guild!*")
    
    log_channel = client.get_channel(1159578058597085194)
    embed = embed_generator(
                title="Unban Submitted", description=f"**PLACEHOLDER DESCRIPTION**\n\nUnban Information:\nUser: {user_snowflake.name}\nModerator: {interaction.user}\n\n Reason: {unban_reason}", color=0xC08C38, fields={},
            ).build()
    reason_str = f"{unban_reason} ({interaction.user.name})"
    unban_check = False
    async for bans_user in interaction.guild.bans():
        if user_snowflake.id == bans_user.user.id:
            unban_check = True
            await interaction.guild.unban(user=user_snowflake, reason=reason_str)
            await interaction.response.send_message(content=f"*{user_snowflake.name} has Successfully Been Unbanned From {interaction.guild.name}!*")
            await log_channel.send(embed=embed)
    if not unban_check:
        await interaction.response.send_message(content=f"*This user could not be unbanned from {interaction.guild.name}. Please double check the User ID and try again!*")

if __name__ == '__main__':
    if config["ENVIRONMENT"] == "PRODUCTION":
        client.run(config["PRODUCTION_BOT_TOKEN"])
    elif config["ENVIRONMENT"] == "DEVELOPMENT":
        client.run(config["DEVELOPMENT_BOT_TOKEN"])