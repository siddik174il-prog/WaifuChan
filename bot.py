
import asyncio
import random
import aiohttp
import discord
from discord.ext import commands, tasks

# =====================================
# WAIFUCHAN CONFIGURATION
# =====================================
import os

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1559647668601491466
AUTO_POST_MINUTES = 5

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True


class WaifuBot(commands.Bot):
    async def setup_hook(self):
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} slash commands!")
        except discord.HTTPException as error:
            print(f"Slash sync error: {error}")


bot = WaifuBot(
    command_prefix="!",
    intents=intents,
    help_command=None
)


# =====================================
# IMAGE API - SFW ONLY
# =====================================

async def get_image(category):
    tags = {
        "waifu": "waifu",
        "neko": "maid",
        "anime": "waifu",
        "hot": "waifu"
    }

    if category not in tags:
        return None

    url = "https://api.waifu.im/images"
    params = {
        "IncludedTags": tags[category],
        "IsNsfw": "False"
    }

    timeout = aiohttp.ClientTimeout(total=20)

    try:
        async with aiohttp.ClientSession(
            timeout=timeout
        ) as session:
            async with session.get(
                url, params=params
            ) as response:

                if response.status != 200:
                    print("Image API status:", response.status)
                    return None

                data = await response.json()
                items = data.get("items", [])

                if not items:
                    return None

                image_url = items[0].get("url")

                if (
                    isinstance(image_url, str)
                    and image_url.startswith("https://")
                ):
                    return image_url

    except (
        aiohttp.ClientError,
        asyncio.TimeoutError,
        ValueError
    ) as error:
        print("Image API error:", error)

    return None


async def post_image(destination, category, title):
    image_url = await get_image(category)

    if not image_url:
        print(f"Could not get image: {category}")
        return False

    embed = discord.Embed(
        title=title,
        color=discord.Color.from_rgb(255, 150, 200)
    )
    embed.set_image(url=image_url)
    embed.set_footer(text="Waifu Chan 🌸")

    try:
        await destination.send(embed=embed)
        return True
    except discord.HTTPException as error:
        print("Discord send error:", error)
        return False


# =====================================
# AUTO POST EVERY 5 MINUTES
# =====================================

@tasks.loop(minutes=AUTO_POST_MINUTES)
async def auto_post_images():
    channel = bot.get_channel(CHANNEL_ID)

    if channel is None:
        try:
            channel = await bot.fetch_channel(CHANNEL_ID)
        except (discord.HTTPException, discord.Forbidden) as error:
            print("Cannot access auto-post channel:", error)
            return

    category = random.choice(["waifu", "neko", "anime"])

    titles = {
        "waifu": "💗 Random Waifu!",
        "neko": "🐱 Random Neko!",
        "anime": "🌸 Random Anime Girl!"
    }

    await post_image(channel, category, titles[category])


@auto_post_images.before_loop
async def before_auto_post():
    await bot.wait_until_ready()


# =====================================
# BOT START
# =====================================

@bot.event
async def on_ready():
    print("=" * 40)
    print(f"💗 Waifu Chan online: {bot.user}")
    print(f"Auto-post channel: {CHANNEL_ID}")
    print(f"Interval: {AUTO_POST_MINUTES} minutes")
    print("=" * 40)

    if not auto_post_images.is_running():
        auto_post_images.start()


# =====================================
# IMAGE COMMANDS
# Hybrid commands work with ! AND /
# =====================================

@bot.hybrid_command(
    name="waifu",
    description="Get a random SFW waifu image!"
)
async def waifu(ctx):
    await post_image(ctx, "waifu", "💗 A Random Waifu!")


@bot.hybrid_command(
    name="neko",
    description="Get a random SFW neko image!"
)
async def neko(ctx):
    await post_image(ctx, "neko", "🐱 Random Neko!")


@bot.hybrid_command(
    name="anime",
    description="Get a random SFW anime image!"
)
async def anime(ctx):
    await post_image(ctx, "anime", "🌸 Random Anime Girl!")


# =====================================
# !HOT ANIME COMMAND
# =====================================

@bot.command(name="hot")
async def hot(ctx, *, topic=""):
    if topic.lower().strip() != "anime":
        await ctx.send("Try `!hot anime` 🌸")
        return

    await post_image(
        ctx,
        "hot",
        "🔥 Hot Anime Style (SFW)!"
    )


# =====================================
# CUTE COMMANDS
# =====================================

@bot.hybrid_command(name="hello", description="Say hello!")
async def hello(ctx):
    await ctx.send("Hiii baby! 💗 Kemon acho? 🌸")


@bot.hybrid_command(name="love", description="Send some love!")
async def love(ctx):
    await ctx.send("Awww! Sending you lots of love! 💗💕")


@bot.hybrid_command(name="hug", description="Get a virtual hug!")
async def hug(ctx):
    await ctx.send("(づ｡◕‿‿◕｡)づ 💗 Big virtual hug!")


@bot.hybrid_command(name="kiss", description="Get a virtual kiss!")
async def kiss(ctx):
    await ctx.send("Mwahhh! 😚💋💕")


@bot.hybrid_command(name="cute", description="Get a compliment!")
async def cute(ctx):
    await ctx.send("You're super cute! 🥺💗✨")


@bot.hybrid_command(name="chat", description="Chat with Waifu Chan!")
async def chat(ctx, *, message: str):
    msg = message.lower()

    if "how are you" in msg or "kemon acho" in msg:
        reply = "Ami bhalo achi! 💗 Tumi kemon acho?"
    elif "i love you" in msg or "love you" in msg:
        reply = "Awww! Sending you a virtual hug! 🤗💕"
    elif "miss you" in msg:
        reply = "I'm here to chat with you! 🌸💗"
    elif "sad" in msg:
        reply = "Ki hoyeche? 🥺 I'm listening."
    elif "hello" in msg or "hi" in msg:
        reply = "Hiii! 💗🌸 Ki korcho?"
    else:
        reply = "Aro bolo! 💕 Ami shunchi. 🥺"

    await ctx.send(reply)


# =====================================
# VOICE COMMANDS
# =====================================

@bot.hybrid_command(name="join", description="Join your voice channel!")
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send("Age voice channel-e join koro! 💗")
        return

    channel = ctx.author.voice.channel

    try:
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect(timeout=20, reconnect=True)

        await ctx.send(f"💗 Joined **{channel.name}**!")

    except (
        discord.Forbidden,
        discord.ClientException,
        asyncio.TimeoutError
    ) as error:
        print("Voice error:", error)
        await ctx.send("VC-te join kora jayni! 🥺")


@bot.hybrid_command(name="leave", description="Leave your voice channel!")
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Bye-bye! 💗🌸")
    else:
        await ctx.send("Ami ekhon kono VC-te nei! 🥺")


# =====================================
# HELP COMMAND
# =====================================

@bot.hybrid_command(name="help", description="Show all commands!")
async def help_command(ctx):
    embed = discord.Embed(
        title="🌸 Waifu Chan Commands",
        description=(
            "**Images:** `!waifu` `!neko` `!anime` `!hot anime`\n"
            "**Slash:** `/waifu` `/neko` `/anime`\n"
            "**Cute:** `/hello` `/love` `/hug` `/kiss` `/cute`\n"
            "**Chat:** `/chat`\n"
            "**Voice:** `/join` `/leave`\n"
            "**Auto-post:** Every 5 minutes 💗"
        ),
        color=discord.Color.from_rgb(255, 150, 200)
    )
    await ctx.send(embed=embed)


# =====================================
# ERROR HANDLING
# =====================================

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return

    print("Prefix command error:", repr(error))

    try:
        await ctx.send("Aww 🥺 Command-e problem hoyeche!")
    except discord.HTTPException:
        pass


@bot.tree.error
async def slash_error(interaction, error):
    print("Slash command error:", repr(error))

    try:
        message = "Aww 🥺 Command-e problem hoyeche!"

        if interaction.response.is_done():
            await interaction.followup.send(
                message, ephemeral=True
            )
        else:
            await interaction.response.send_message(
                message, ephemeral=True
            )
    except discord.HTTPException:
        pass


# =====================================
# RUN BOT
# =====================================

if __name__ == "__main__":
    if TOKEN == "PASTE_YOUR_BOT_TOKEN_HERE":
        raise RuntimeError(
            "Put your Discord bot token in TOKEN first!"
        )

    bot.run(TOKEN)
