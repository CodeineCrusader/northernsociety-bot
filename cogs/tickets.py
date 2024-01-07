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
from interactions import input_modal, ban_input_other
from embed_generator import embed_generator

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

class tickets(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="support", description="Create Support Ticket Embed")
    @app_commands.checks.has_permissions(administrator=True)
    async def support(self, interaction: discord.Interaction):
        if not interaction.guild_id == 1158271879556104204:
            return interaction.response.send_message("You need to be in the main server to execute this command!", ephemeral=True)
        channel = self.client.get_channel(1159362455785443348)
        fields = {"Server Support": "PLACEHOLDER", "Player Report": "PLACEHOLDER", "Staff Report": "PLACEHOLDER"}
        generator = embed_generator(
            title="North Society Ticket Booth",
            description="*Description Coming Soon*",
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
                view = discord.ui.View()
                await interaction.response.send_message(f"*Your ticket has been created! Please navigate to <#{channel.id}> to continue your support request.*", ephemeral=True)
                await channel.send(content=f"{interaction.user.mention} <Support Ping>", embed=embed, view=view)
            elif "pr" in buttonPressed:
                channel = await guild.create_text_channel(f"{interaction.user.name}-player", category=report_category)
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
                view = discord.ui.View()
                await interaction.response.send_message(f"*Your ticket has been created! Please navigate to <#{channel.id}> to continue your report.*", ephemeral=True)
                await channel.send(content=f"{interaction.user.mention} <Staff Ping>", embed=embed, view=view)
            elif "sr" in buttonPressed:
                channel = await guild.create_text_channel(f"{interaction.user.name}-staff", category=report_category)
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
                view = discord.ui.View()
                await interaction.response.send_message(f"*Your ticket has been created! Please navigate to <#{channel.id}> to continue your report.*", ephemeral=True)
                await channel.send(content=f"{interaction.user.mention} <Staff Ping>", embed=embed, view=view)

        except AttributeError or KeyError:
            pass


async def setup(client: commands.Bot):
    await client.add_cog(tickets(client))
    logger.info(f"cogs.tickets.tickets.py Successfully Loaded!")