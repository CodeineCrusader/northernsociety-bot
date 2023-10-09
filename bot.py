import platform
import discord
from discord import app_commands, ui
from discord.ext import commands, tasks
from discord.utils import get, setup_logging
from discord.ui import Button, View
import logging
import time
import os
import colorama
import random
from dotenv import dotenv_values
import jishaku

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


@tasks.loop(minutes=1)
async def status():
    choices = [
        discord.Activity(type=discord.ActivityType.listening, name='Closely'),
    ]
    chosen = random.choice(choices)
    await client.change_presence(activity=chosen)


class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or(config["prefix"]), case_insensitive=True, intents=discord.Intents.all())
        self.cogs_list = ['jishaku']

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

if __name__ == '__main__':
    if config["ENVIRONMENT"] == "PRODUCTION":
        client.run(config["PRODUCTION_BOT_TOKEN"])
    elif config["ENVIRONMENT"] == "DEVELOPMENT":
        client.run(config["DEVELOPMENT_BOT_TOKEN"])