import logging
import time

import discord
from discord import app_commands
from discord.ext import commands

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

class mod_log_handling(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.moderation_list = [
            discord.AuditLogAction.ban,
            discord.AuditLogAction.unban,
            discord.AuditLogAction.kick,
            discord.AuditLogAction.member_prune,
            discord.AuditLogAction.member_update,
            discord.AuditLogAction.member_disconnect
        ]
    # *         This section will be handling mod logs done by the user directly, and not through the bot (not through the command the bot provides)
    # ?         Unban, Ban, Timeout, Server Mute, Server Deafen ...
    # TODO:     Plan to Upload Moderation Data for Logging Purposes
    # !         If the action is done by discord.Client.user.name (bot client) then return
    # !         The uploading of moderation data by the bot will be handled when the user is moderated THROUGH the bot


    @commands.Cog.listener()
    async def on_audit_log_entry_create(self, entry) -> None:
        print(entry.target)
        if entry.action not in self.moderation_list:
            return

        # TODO: Send data to database to be saved
        # * Below are the columns of information being sent to the database
        # * uid | mid | action | reason | timestamp
        # ? UID - ID of the Violator
        # ? MID - ID of the Moderator
        # ? Action - Action Used Against Violator
        # ? Reason - Reason for Action Being Taken
        # ? Timestamp - Timestamp of the Action being Taken Against the Violator


async def setup(client: commands.Bot):
    await client.add_cog(mod_log_handling(client))
    logger.info(f"cogs.moderation.mod_log_handling.py Successfully Loaded!")