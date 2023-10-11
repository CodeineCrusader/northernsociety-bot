import discord
import datetime


class embed_generator:
    def __init__(self, title : str = None, description : str = None, footer : str = None, footer_icon_url : str = None, thumbnail : str = None, fields : dict = None, author : str = None, author_icon_url : str = None, color : hex = None, timezone : datetime.datetime = None, image_url : str = None):
        self.title = title
        self.description = description
        self.color = color
        self.footer = footer
        self.footer_icon_url = footer_icon_url
        self.author = author
        self.author_icon_url = author_icon_url
        self.fields = fields
        self.thumbnail = thumbnail
        self.timezone = timezone
        self.image_url = image_url
        self.fieldTitle = []
        self.fieldDesc = []

    def build(self):
        count = 0
        for item in self.fields.values():
            self.fieldDesc.append(item)
        self.fieldTitle = list(self.fields)
        embed = discord.Embed(title=self.title, description=self.description, color=self.color)
        embed.timestamp = self.timezone
        embed.set_thumbnail(url=self.thumbnail)
        embed.set_footer(text=self.footer, icon_url=self.footer_icon_url)
        if self.image_url:
            embed.set_image(url=str(self.image_url))
        if self.author and self.author_icon_url:
            embed.set_author(name=self.author, icon_url=self.author_icon_url)
        for _ in self.fieldTitle:
            embed.add_field(name=str(self.fieldTitle[count]), value=str(self.fieldDesc[count]), inline=False)
            count += 1
        return embed
