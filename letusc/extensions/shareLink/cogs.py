import json
import discord
from discord import SlashCommandGroup, option
from discord.ext import commands


from .bot import ShareLinkClient
from ...logger import get_logger

logger = get_logger(__name__)


def split_list(list, chunk_size: int):
    for i in range(0, len(list), chunk_size):
        yield list[i : i + chunk_size]


def parse_link(link: str) -> str:
    link = link.replace("twitter.com", "fxtwitter.com")
    link = link.replace("x.com", "fxtwitter.com")
    return link


def extract_twitter_id(link: str) -> str:
    twitter_id = link.split("/")[3]
    return twitter_id


# known_ids.json
def load_known_ids():
    with open("known_ids.json", "r") as file:
        data = json.load(file)
        return data["knowns"]


def add_known_id(twitter_id: str, thread_id: str):
    data = load_known_ids()
    data[twitter_id] = {"thread_id": thread_id}
    with open("known_ids.json", "w") as file:
        json.dump({"knowns": data}, file, indent=4)


# guilds.json
def load_available_guilds():
    with open("guilds.json", "r") as file:
        data = json.load(file)
        return data["guilds"]


def add_available_guild(guild_id: str, channel_id: str):
    data = load_available_guilds()
    data[guild_id] = {"channel_id": channel_id}
    with open("guilds.json", "w") as file:
        json.dump({"guilds": data}, file, indent=4)


def remove_available_guild(guild_id: str):
    data = load_available_guilds()
    del data[str(guild_id)]
    with open("guilds.json", "w") as file:
        json.dump({"guilds": data}, file, indent=4)


def is_available_guild(guild_id: str):
    data = load_available_guilds()
    return str(guild_id) in data


# config.json
def load_config():
    with open("config.json", "r") as file:
        data = json.load(file)
        return data


def load_user_config(user_id: str):
    data = load_config()
    return data["users"][user_id] if (user_id in data["users"]) else {}


def add_user_config(user_id: str, config: dict):
    data = load_config()
    data["users"][user_id] = config
    with open("config.json", "w") as file:
        json.dump(data, file, indent=4)


def remove_user_config(user_id: str):
    data = load_config()
    del data["users"][user_id]
    with open("config.json", "w") as file:
        json.dump(data, file, indent=4)


# action
async def send_link(user_id: str, link: str, thread_id=None) -> bool:
    bot = await ShareLinkClient.get_client()
    user_config = load_user_config(user_id)
    guild_id = user_config["guild_id"]
    if is_available_guild(guild_id):
        if not thread_id:
            thread_id = load_known_ids()[extract_twitter_id(link)]["thread_id"]
        thread = bot.get_channel(int(thread_id))
        assert isinstance(thread, discord.Thread)
        message = await thread.send(parse_link(link))
        channel_id = load_available_guilds()[guild_id]["channel_id"]
        channel = bot.get_channel(int(channel_id))
        assert isinstance(channel, discord.TextChannel)
        await channel.send(
            f"Shared **`@{extract_twitter_id(link)}`**'s Post: {message.jump_url} \n\n{parse_link(link)}"
        )
        return True
    else:
        return False


class UseDifferentIDButton(discord.ui.Button):
    def __init__(
        self, twitter_id: str, link: str, known_ids: list[str], custom_id: str, key: int
    ):
        super().__init__(
            label=f"IDs {key}", style=discord.ButtonStyle.blurple, custom_id=custom_id
        )
        self.twitter_id = twitter_id
        self.link = link
        self.known_ids = known_ids

    async def callback(self, interaction: discord.Interaction):
        if len(self.known_ids) > 0:
            await interaction.response.edit_message(
                content="Please select a different Twitter ID.",
                view=SelectIDView(self.known_ids, self.link),
            )
        else:
            await interaction.response.edit_message(
                content="Please provide a different Twitter ID.", view=None
            )


class CheckSelectionEmbed(discord.Embed):
    def __init__(self, known_ids: list[str], link: str):
        super().__init__(
            title="Select a Twitter ID",
            description="Please select a Twitter ID.",
            color=discord.Color.blurple(),
        )
        self.known_ids = known_ids
        self.link = link
        known_ids_chunks = list(split_list(self.known_ids, 20))
        i = 0
        for chunk in known_ids_chunks:
            self.add_field(name=f"IDs {i}", value=", ".join(chunk), inline=True)
            i += 1


class UnknownIDView(discord.ui.View):
    def __init__(self, twitter_id: str, link: str):
        super().__init__()
        self.twitter_id = twitter_id
        self.link = link

        known_ids = load_known_ids()
        known_ids_chunks = list(split_list(list(known_ids.keys()), 20))
        i = 0
        for chunk in known_ids_chunks:
            self.add_item(
                UseDifferentIDButton(
                    twitter_id, link, chunk, custom_id=f"use_different_id_{i}", key=i
                )
            )
            i += 1

    @discord.ui.button(
        label="Add ID", style=discord.ButtonStyle.green, custom_id="add_id"
    )
    async def add_id(self, button: discord.ui.Button, interaction: discord.Interaction):
        bot = await ShareLinkClient.get_client()
        assert interaction.user
        user_config = load_user_config(str(interaction.user.id))
        guild_id = user_config["guild_id"]
        guild_config = load_available_guilds()[guild_id]
        channel_id = guild_config["channel_id"]
        channel = bot.get_channel(channel_id)
        assert isinstance(channel, discord.TextChannel)
        thread = await channel.create_thread(
            name=f"@{self.twitter_id}",
            auto_archive_duration=10080,
            reason="New Twitter ID",
            type=discord.ChannelType.public_thread,
        )
        await interaction.response.edit_message(
            content=f"Added ID: {self.twitter_id} with thread {thread.mention}",
            view=None,
        )
        await thread.send(f"Auto-mentioning <@{interaction.user.id}>")
        add_known_id(self.twitter_id, str(thread.id))
        await send_link(str(interaction.user.id), self.link)


class SelectIDView(discord.ui.View):
    def __init__(self, known_ids: list[str], link: str):
        super().__init__()
        self.known_ids = known_ids
        self.link = link
        self.select.placeholder = "known IDs"
        self.select.options = [
            discord.SelectOption(label=user_id, value=user_id)
            for user_id in self.known_ids
        ]

    @discord.ui.select(placeholder="known IDs")
    async def select(self, select: discord.ui.Select, interaction: discord.Interaction):
        assert interaction.user
        await send_link(
            str(interaction.user.id),
            self.link,
            load_known_ids()[select.values[0]]["thread_id"],
        )
        await interaction.response.edit_message(
            content=f"Selected ID: {select.values[0]}", view=None
        )


class ShareLink(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    share = SlashCommandGroup(name="share", description="Share a link with the server")
    guild = SlashCommandGroup(
        name="guild", description="Manage the guilds that can use this bot"
    )
    config = SlashCommandGroup(name="config", description="Configure the bot")

    @share.command(name="link", description="Share a link with the server")
    @option(name="link", description="The link to share", required=True)
    async def share_link(self, ctx, link: str):
        twitter_id = extract_twitter_id(link)
        known_ids = load_known_ids()
        if twitter_id in known_ids:
            await ctx.respond("Trying to send link...")
            await send_link(str(ctx.author.id), link)
        else:
            await ctx.respond(
                "This Twitter ID is not known. Would you like to add it or use a different ID?",
                view=UnknownIDView(twitter_id, link),
            )

    @guild.command(
        name="add", description="Add a guild to the list of available guilds"
    )
    async def add_guild(self, ctx):
        add_available_guild(str(ctx.guild.id), ctx.channel.id)
        await ctx.respond("Added guild & channel to the list of available guilds.")

    @guild.command(
        name="remove", description="Remove a guild from the list of available guilds"
    )
    async def remove_guild(self, ctx):
        remove_available_guild(str(ctx.guild.id))
        await ctx.respond("Removed guild from the list of available guilds.")

    @config.command(name="set_guild", description="Set the guild for a user")
    @option(name="guild_id", description="The guild to set", required=True)
    async def set_guild(self, ctx, guild_id: str):
        user_config = load_user_config(ctx.author.id)
        user_config["guild_id"] = guild_id
        add_user_config(ctx.author.id, user_config)
        await ctx.respond("Set guild for user.")

    @config.command(name="remove", description="Remove a user from the config")
    async def remove_user(self, ctx):
        remove_user_config(ctx.author.id)
        await ctx.respond("Removed user from config.")

    @discord.Cog.listener("on_message")
    async def on_message(self, message):
        if message.author.bot:
            return
        if not isinstance(message.channel, discord.DMChannel):
            return
        if message.content.startswith(
            "https://twitter.com/"
        ) or message.content.startswith("https://x.com/"):
            twitter_id = extract_twitter_id(message.content)
            known_ids = load_known_ids()
            if twitter_id in known_ids:
                await send_link(str(message.author.id), message.content)
            else:
                await message.channel.send(
                    f"This Twitter ID is not known. Would you like to add it or use a different ID?",
                    view=UnknownIDView(twitter_id, message.content),
                    embed=CheckSelectionEmbed(list(known_ids.keys()), message.content),
                )
