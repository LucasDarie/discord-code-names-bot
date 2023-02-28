import interactions
import os
from dotenv import load_dotenv
from GameList import GameList
import asyncio
from Language import Language
from ColorCard import ColorCard
from CodeGameExceptions import *

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
GUILD_ID = os.getenv('GUILD_ID')

bot = interactions.Client(token=BOT_TOKEN, default_scope=GUILD_ID)

GAME_LIST = GameList()



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

@bot.command()
async def display(ctx: interactions.CommandContext):
    """Display the grid depending on your role"""
    await ctx.send("Hi there!")

@bot.command()
@interactions.option(description="Chose the language of the game")
async def create(ctx: interactions.CommandContext, language:str):
    """Create a game of Code Names"""
    lang = Language.FR if language == "FR" else Language.EN
    try:
        await GAME_LIST.create_game(language=lang, channel_id=ctx.channel_id, creator_id=ctx.user.id, guild_id=ctx.guild_id)
        await ctx.send(f"({lang.value}) Game created by user {ctx.user.id} in channel {ctx.channel.id}")
    except GameInChannelAlreadyCreated:
        ctx.send("A game is already created")
        
@bot.command()
@interactions.option(description="Chose your team !")
async def join(ctx: interactions.CommandContext, team:str):
    """Join a game of Code Names"""
    color = ColorCard.BLUE if team == "BLUE" else ColorCard.RED
    try:
        game = await GAME_LIST.get_game(ctx.channel_id)
        await game.join(ctx.user, team_color=color)
        await ctx.send(f"You join the {color.value} team !", ephemeral=True)
    except GameNotFound:
        await ctx.send("No game created. Use `/create` to create a game !", ephemeral=True)

bot.start()