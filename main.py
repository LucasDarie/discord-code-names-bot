import interactions
import os
from dotenv import load_dotenv
from GameList import GameList
import asyncio
from Language import Language
from ColorCard import ColorCard
from CodeGameExceptions import *
from Game import Game, State
from ButtonLabel import ButtonLabel

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
GUILD_ID = os.getenv('GUILD_ID')

bot = interactions.Client(token=BOT_TOKEN, default_scope=GUILD_ID)#, presence=interactions.ClientPresence(status=interactions.StatusType.INVISIBLE))

GAME_LIST = GameList()

def get_team_message(game:Game, color:ColorCard, withSpy:bool=True) -> str:
    """return the list of player in a specific team 

    Args:
        game (Game): the game
        color (ColorCard): the team's color
        withSpy (bool, optional): chose to display or not the spy of the team. Defaults to True.

    Returns:
        str: the list of player @ for discord uses, seperatded by commas
    """
    return str([f"<@{p.user.id}>" for p in game.teams[color] if withSpy or not p.isSpy]).translate({ord('['):None, ord('\''):None, ord(']'):None})

def players_turn_message(game:Game) -> str:
    return f"{game.color_state.display()} PLAYERS' turn: {get_team_message(game, game.color_state, withSpy=False)}\
        \nHint: `{game.last_word_suggested}`\nNumber of tries remaining: `{game.last_number_hint}{' (+1 bonus)`' if game.bonus_proposition else '`'}\
        \n`/guess` to guess a word of your team's color"

def get_display_button(language:Language) -> list[interactions.Button]:
    return [interactions.Button(
            custom_id=ButtonLabel.DISPLAY_GRID_BUTTON.value,
            style=interactions.ButtonStyle.SUCCESS,
            label=ButtonLabel.DISPLAY_GRID_BUTTON.label(language),
        )]

def get_skip_button(language:Language) -> list[interactions.Button]:
        return [interactions.Button(
                custom_id=ButtonLabel.SKIP_BUTTON.value,
                style=interactions.ButtonStyle.SUCCESS,
                label=ButtonLabel.SKIP_BUTTON.label(language),
            )]


def state_message(game:Game) -> str:

    match game.state:
        case State.WAITING:
            return "Waiting for game creator to start the game"
        case State.SPY:
            return f"{game.color_state.display()} SPY's turn : <@{game.spies[game.color_state].user.id}>\n`/display` to see your own grid\n`/suggest` to suggest a hint to your teammates"
        case State.PLAYER:
            return players_turn_message(game)
        case State.WIN:
            return f"{game.color_state.display()} TEAM WIN! GG {get_team_message(game, color=game.color_state)}"



def state_component(game:Game) -> list[interactions.Button] | None:
    match game.state:
        case State.WAITING:
            return get_join_buttons(game.language)
        case State.SPY:
            return get_display_button(game.language)
        case State.PLAYER:
            # don't display skip button after /suggest message
            if game.one_word_found:
                return get_skip_button(game.language)
        case _:
            return None


@bot.user_command(name="User Command")
async def test(ctx: interactions.CommandContext):
    await ctx.send(f"You have applied a command onto user {ctx.target.user.username}!")



@bot.command()
@bot.component("display_grid_button_id")
async def display(ctx: interactions.CommandContext):
    """Display the grid depending on your role"""
    try:
        game = await GAME_LIST.get_game(ctx.channel_id, language=Language.get_discord_equivalent(ctx.locale))
        image = interactions.File(game.get_user_image_path(ctx.user))
        await ctx.send(files=image, ephemeral=True)
    except (GameNotFound, GameNotStarted, NotInGame, FileNotFoundError) as e:
        await ctx.send(e.message, ephemeral=True)



def get_create_message(game:Game):
    return f"[{str(game.language.value).upper()}] {game.language.display()} Game created by <@{game.creator_id}>\
                \n\
                \n{ColorCard.BLUE.display()} team : {get_team_message(game, color=ColorCard.BLUE)}\
                \n{ColorCard.RED.display()} team : {get_team_message(game, color=ColorCard.RED)}"



def get_join_buttons(language:Language, game:Game) -> list[interactions.Button]:
    buttons = [
        interactions.Button(
            custom_id=ButtonLabel.get_by_color(team_color).value,
            style=interactions.ButtonStyle.PRIMARY,
            label=ButtonLabel.get_by_color(team_color).label(language)
        )
        for team_color in game.team_colors
    ]
    buttons.extend([
        interactions.Button(
            custom_id=ButtonLabel.LEAVE_BUTTON.value,
            style=interactions.ButtonStyle.DANGER,
            label=ButtonLabel.LEAVE_BUTTON.label(language)
        ),
        interactions.Button(
            custom_id=ButtonLabel.START_BUTTON.value,
            style=interactions.ButtonStyle.SUCCESS,
            label=ButtonLabel.START_BUTTON.label(language)
        ),
    ])
    return buttons



@bot.command()
@interactions.option(
    description="Chose the language of the game",
    type=interactions.OptionType.STRING,
    name="language",
    required=True,
    choices=[
        interactions.Choice(name="French", value=Language.FR.value),
        interactions.Choice(name="English", value=Language.EN.value)
    ] 
)
async def create(ctx: interactions.CommandContext, language:str):
    """Create a game of Code Names"""
    lang = Language.FR if language == Language.FR.value else Language.EN
    try:
        game = await GAME_LIST.create_game(language=lang, channel_id=ctx.channel_id, creator_id=ctx.user.id, guild_id=ctx.guild_id)
        await ctx.send(content=get_create_message(game), components=state_component(game))
    except GameInChannelAlreadyCreated as e:
        await ctx.send(e.message, ephemeral=True)



@bot.command()
async def delete(ctx: interactions.CommandContext):
    """Create a game of Code Names"""
    try:
        await GAME_LIST.delete_game(channel_id=ctx.channel_id, language=Language.get_discord_equivalent(ctx.locale))
        await ctx.send(f"{ctx.user.username} deleted the game")
    except GameNotFound as e:
        await ctx.send(e.message, ephemeral=True)


async def join_team(
        ctx: interactions.ComponentContext | interactions.CommandContext, 
        team:ColorCard, 
        message:interactions.Message=None):
    color = ColorCard.BLUE if team == ColorCard.BLUE.value else ColorCard.RED
    try:
        game = await GAME_LIST.get_game(ctx.channel_id, language=Language.get_discord_equivalent(ctx.locale))
        await game.join(ctx.user, team_color=color)
        if(message != None):
            await message.edit(content=get_create_message(game), components=state_component(game))
            await ctx.edit(ctx.message.content)
        else:
            await ctx.send(f"{ctx.user.username} join the {color.display()} team !")
    except (GameNotFound, GameAlreadyStarted) as e:
        await ctx.send(e.message, ephemeral=True)



@bot.command()
@interactions.option(
    description="Chose your team !",
    type=interactions.OptionType.STRING,
    name="team",
    required=True,
    choices=[
        interactions.Choice(name="BLUE", value=ColorCard.BLUE.value),
        interactions.Choice(name="RED", value=ColorCard.RED.value)
    ] 
)
async def join(ctx: interactions.CommandContext, team:str):
    """Join a game of Code Names"""
    await join_team(ctx, team)



@bot.component("red_join_button_id")
async def on_login_red_click(ctx:interactions.ComponentContext):
    await join_team(ctx, team=ColorCard.RED.value, message=ctx.message)



@bot.component("blue_join_button_id")
async def on_login_blue_click(ctx:interactions.CommandContext):
    await join_team(ctx, team=ColorCard.BLUE.value, message=ctx.message)



@bot.command()
@bot.component("leave_button_id")
async def leave(ctx: interactions.CommandContext):
    """leave a game that did not start"""
    try:
        game = await GAME_LIST.get_game(ctx.channel_id, language=Language.get_discord_equivalent(ctx.locale))
        await game.leave(ctx.user)
        if(ctx.message != None):
            await ctx.message.edit(content=get_create_message(game), components=state_component(game))
            await ctx.send(f"You left the game", ephemeral=True)
        else:
            await ctx.send(f"{ctx.user.username} left the game")
    except (GameNotFound, NotInGame, GameAlreadyStarted) as e:
        await ctx.send(e.message, ephemeral=True)



@bot.command()
@bot.component("start_button_id")
async def start(ctx: interactions.CommandContext):
    """Start the game of Code Names"""
    try:
        game = await GAME_LIST.get_game(ctx.channel_id, language=Language.get_discord_equivalent(ctx.locale))
        await game.start(ctx.user.id)
        color = game.starting_team_color
        start_message = "🔲 `STARTS`"
        image = interactions.File(game.get_image_path())
        await ctx.send(f"The `Code Names` game is starting LET'S GOOO!\
                       \n\
                       \n{ColorCard.BLUE.display()} SPY: <@{game.spies[ColorCard.BLUE].user.id}>{start_message if color == ColorCard.BLUE else ''}\
                       \n{ColorCard.RED.display()} SPY: <@{game.spies[ColorCard.RED].user.id}>{start_message if color == ColorCard.RED else ''}\
                       \n\
                       \n{state_message(game)}",
                    components=state_component(game),
                    files=image
        )
        # await ctx.send(state_message(game), components=state_component(game))
    except (GameNotFound, NotGameCreator, GameAlreadyStarted, NotEnoughPlayerInTeam) as e:
        await ctx.send(e.message, ephemeral=True)



@bot.command()
@interactions.option(description="A hint that will help your teammates to guess the words of your color. Use `/rules` for more info")
@interactions.option(description="The number of tries your teammates will have to guess the words")
async def suggest(ctx: interactions.CommandContext, hint:str, number_of_try:int):
    """Suggest a hint to help your team to guess words. Provide also a number of try"""
    try:
        game = await GAME_LIST.get_game(ctx.channel_id, language=Language.get_discord_equivalent(ctx.locale))
        await game.suggest(ctx.user, hint, number_of_try)

        await ctx.send(state_message(game), components=state_component(game))

    except (GameNotFound, GameNotStarted, NotInGame, NotYourRole, NotYourTurn, WrongHintNumberGiven, WordInGrid) as e:
        await ctx.send(e.message, ephemeral=True)



@bot.command()
async def guess(ctx: interactions.CommandContext):
    """This description isn't seen in UI (yet?)"""
    pass

@guess.subcommand()
@interactions.option(description="guess a word by using the suggested hint")
async def word(ctx: interactions.CommandContext, word: str):
    """Propose a word present in the grid"""
    await guess_by_func(ctx=ctx, word=word)
    

@guess.subcommand()
@interactions.option(description="A descriptive description")
async def card_id(ctx: interactions.CommandContext, card_id: int):
    """Propose a word card number present in the grid"""
    await guess_by_func(ctx=ctx, card_id=card_id)


async def guess_by_func(ctx: interactions.CommandContext, word:str=None, card_id:int=None):
    try:
        game = await GAME_LIST.get_game(ctx.channel_id, language=Language.get_discord_equivalent(ctx.locale))
        if word == None and card_id != None:
            (card_color, word_found) = await game.guess_by_card_id(ctx.user, card_id)
        elif word != None and card_id == None:
            (card_color, word_found) = await game.guess_by_word(ctx.user, word)
        else:
            # can't happen
            await ctx.send("An error occured. Try again")
            return
        image = interactions.File(game.get_image_path(isSpy=(game.state in [State.BLUE_WIN, State.RED_WIN])))
        await ctx.send(f"The word {word_found} was {card_color.display()}\
                       \n{ColorCard.BLUE.display()} words remaining : `{game.card_grid.remaining_words_count[ColorCard.BLUE]}`\
                       \n{ColorCard.RED.display()}  words remaining : `{game.card_grid.remaining_words_count[ColorCard.RED]}`\
                       \n\
                       \n{state_message(game)}", 
                       files=image, 
                       components=state_component(game)
        )
        if game.state in [State.BLUE_WIN, State.RED_WIN]:
            await GAME_LIST.delete_game(game.channel_id, language=Language.get_discord_equivalent(ctx.locale))

    except (GameNotFound, GameNotStarted, NotInGame, NotYourRole, NotYourTurn, WordNotInGrid, WrongCardIdNumberGiven) as e:
        await ctx.send(e.message, ephemeral=True)

@bot.command()
@bot.component("skip_button_id")
async def skip(ctx: interactions.CommandContext):
    """End the player turn if at least one word is proposed"""
    try:
        game = await GAME_LIST.get_game(ctx.channel_id, language=Language.get_discord_equivalent(ctx.locale))
        await game.skip(ctx.user)
        await ctx.send(f"{ctx.user.username} skipped their turn...\
                       \n\
                       \n{state_message(game)}", components=state_component(game))
    except (GameNotFound, GameNotStarted, NotInGame, NotYourRole, NotYourTurn, NoWordGuessed) as e:
        await ctx.send(e.message, ephemeral=True)
    


bot.start()