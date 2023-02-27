import interactions
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
GUILD_ID = os.getenv('GUILD_ID')

bot = interactions.Client(token=BOT_TOKEN, default_scope=GUILD_ID)

@bot.command()
async def find(ctx: interactions.CommandContext):
    """This description isn't seen in UI (yet?)"""
    pass

@find.subcommand()
@interactions.option(description="Find a word by using the suggested hint")
async def word(ctx: interactions.CommandContext, option: str = None):
    """Propose a word present in the grid"""
    await ctx.send(f"You selected the word sub command and put in {option}")

@find.subcommand()
@interactions.option(description="A descriptive description")
async def number(ctx: interactions.CommandContext, second_option: int):
    """Propose a word card number present in the grid"""
    await ctx.send(f"You selected the number sub command and put in {second_option}")

@bot.user_command(name="User Command")
async def test(ctx: interactions.CommandContext):
    await ctx.send(f"You have applied a command onto user {ctx.target.user.username}!")



bot.start()