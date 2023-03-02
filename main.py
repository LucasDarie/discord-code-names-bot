import interactions
import os
from dotenv import load_dotenv
from GameList import GameList
import asyncio
from Language import Language
from ColorCard import ColorCard
from CodeGameExceptions import *
from Game import Game, State

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
GUILD_ID = os.getenv('GUILD_ID')

bot = interactions.Client(token=BOT_TOKEN, default_scope=GUILD_ID, presence=interactions.ClientPresence(status=interactions.StatusType.INVISIBLE))

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
    return f"{game.state.color().display()} PLAYERS' turn: {get_team_message(game, game.state.color(), withSpy=False)}\
        \nHint: `{game.last_word_suggested}`\nNumber of tries remaining: `{game.last_number_hint}{' (+1 bonus)`' if game.bonus_proposition else '`'}\
        \n`/guess` to guess a word of your team's color"

def get_display_button() -> list[interactions.Button]:
    return [interactions.Button(
            custom_id="display_button_id",
            style=interactions.ButtonStyle.SUCCESS,
            label="DISPLAY GRID",
        )]

def get_skip_button() -> list[interactions.Button]:
        return [interactions.Button(
                custom_id="skip_button_id",
                style=interactions.ButtonStyle.SUCCESS,
                label="SKIP",
            )]


def state_message(game:Game) -> str:

    match game.state:
        case State.WAITING:
            return "Waiting for game creator to start the game"
        case State.BLUE_SPY | State.RED_SPY:
            return f"{game.state.color().display()} SPY's turn : <@{game.spies[game.state.color()].user.id}>\n`/display` to see your own grid\n`/suggest` to suggest a hint to your teammates"
        case State.BLUE_PLAYER | State.RED_PLAYER:
            return players_turn_message(game)
        case State.BLUE_WIN | State.RED_WIN:
            return f"{game.state.color().display()} TEAM WIN! GG {get_team_message(game, color=game.state.color())}"



def state_component(game:Game) -> list[interactions.Button] | None:
    match game.state:
        case State.WAITING:
            return get_join_buttons()
        case State.BLUE_SPY | State.RED_SPY:
            return get_display_button()
        case State.BLUE_PLAYER | State.RED_PLAYER:
            # don't display skip button after /suggest message
            if game.one_word_found:
                return get_skip_button()
        case _:
            return None


@bot.user_command(name="User Command")
async def test(ctx: interactions.CommandContext):
    await ctx.send(f"You have applied a command onto user {ctx.target.user.username}!")



@bot.command()
@bot.component("display_button_id")
async def display(ctx: interactions.CommandContext):
    """Display the grid depending on your role"""
    try:
        game = await GAME_LIST.get_game(ctx.channel_id)
        image = interactions.File(game.get_user_image_path(ctx.user))
        await ctx.send(files=image, ephemeral=True)
    except GameNotFound:
        await ctx.send("No game created. Use `/create` to create a game !", ephemeral=True)
    except GameNotStarted:
        await ctx.send("The game did not start")
    except NotInGame:
        await ctx.send("You are not in the game")
    except FileNotFoundError:
        await ctx.send("Error : Image not found")



def get_create_message(game:Game):
    return f"[{str(game.language.value).upper()}] {game.language.display()} Game created by <@{game.creator_id}>\
                \n\
                \n{ColorCard.BLUE.display()} team : {get_team_message(game, color=ColorCard.BLUE)}\
                \n{ColorCard.RED.display()} team : {get_team_message(game, color=ColorCard.RED)}"



def get_join_buttons() -> list[interactions.Button]:
    return [
        interactions.Button(
            custom_id="blue_join_button_id",
            style=interactions.ButtonStyle.PRIMARY,
            label=f"{ColorCard.BLUE.value} TEAM!",
        ),
        interactions.Button(
            custom_id="red_join_button_id",
            style=interactions.ButtonStyle.DANGER,
            label=f"{ColorCard.RED.value} TEAM!",
        ),
        interactions.Button(
            custom_id="leave_button_id",
            style=interactions.ButtonStyle.SECONDARY,
            label=f"LEAVE GAME",
        ),
        interactions.Button(
            custom_id="start_button_id",
            style=interactions.ButtonStyle.SUCCESS,
            label=f"START GAME",
        ),
    ]



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
    except GameInChannelAlreadyCreated:
        await ctx.send("A game is already created in this channel", ephemeral=True)



@bot.command()
async def delete(ctx: interactions.CommandContext):
    """Create a game of Code Names"""
    try:
        await GAME_LIST.delete_game(channel_id=ctx.channel_id)
        await ctx.send(f"{ctx.user.username} deleted the game")
    except GameNotFound:
        await ctx.send("There is currently no game in this channel", ephemeral=True)


async def join_team(
        ctx: interactions.ComponentContext | interactions.CommandContext, 
        team:ColorCard, 
        message:interactions.Message=None):
    color = ColorCard.BLUE if team == ColorCard.BLUE.value else ColorCard.RED
    try:
        game = await GAME_LIST.get_game(ctx.channel_id)
        await game.join(ctx.user, team_color=color)
        if(message != None):
            await message.edit(content=get_create_message(game), components=get_join_buttons())
            await ctx.edit(ctx.message.content)
        else:
            await ctx.send(f"{ctx.user.username} join the {color.display()} team !")
    except GameNotFound:
        await ctx.send("No game created. Use `/create` to create a game !", ephemeral=True)
    except GameAlreadyStarted:
        await ctx.send("The game has already started")



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
        game = await GAME_LIST.get_game(ctx.channel_id)
        await game.leave(ctx.user)
        if(ctx.message != None):
            await ctx.message.edit(content=get_create_message(game), components=get_join_buttons())
            await ctx.send(f"You left the game", ephemeral=True)
        else:
            await ctx.send(f"{ctx.user.username} left the game")
    except GameNotFound:
        await ctx.send("No game created. Use `/create` to create a game !", ephemeral=True)
    except NotInGame:
        await ctx.send("You are not in the game", ephemeral=True)
    except GameAlreadyStarted:
        await ctx.send("The game has already started")



@bot.command()
@bot.component("start_button_id")
async def start(ctx: interactions.CommandContext):
    """Start the game of Code Names"""
    try:
        game = await GAME_LIST.get_game(ctx.channel_id)
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
    except GameNotFound:
        await ctx.send("No game created. Use `/create` to create a game !", ephemeral=True)
    except NotGameCreator:
        await ctx.send("You are not the game creator, you can not start the game", ephemeral=True)
    except GameAlreadyStarted:
        await ctx.send("The game has already started", ephemeral=True)
    except NotEnoughPlayerInTeam:
        await ctx.send("Both teams need to have at least 2 players each", ephemeral=True)



@bot.command()
@interactions.option(description="A hint that will help your teammates to guess the words of your color. Use `/rules` for more info")
@interactions.option(description="The number of tries your teammates will have to guess the words")
async def suggest(ctx: interactions.CommandContext, hint:str, number_of_try:int):
    """Suggest a hint to help your team to guess words. Provide also a number of try"""
    try:
        game = await GAME_LIST.get_game(ctx.channel_id)
        await game.suggest(ctx.user, hint, number_of_try)

        await ctx.send(state_message(game), components=state_component(game))

    except GameNotFound:
        await ctx.send("No game created. Use `/create` to create a game !", ephemeral=True)
    except GameNotStarted:
        await ctx.send("The game did not start", ephemeral=True)
    except NotInGame:
        await ctx.send("You are not in the game", ephemeral=True)
    except NotYourRole:
        await ctx.send("You are not a spy you can not use this command !", ephemeral=True)
    except NotYourTurn as e:
        await ctx.send(f"{e}", ephemeral=True)
    except WrongHintNumberGiven:
        await ctx.send("the `number of try` given is smaller than 0, it must be `> 0`", ephemeral=True)
    except WordInGrid:
        await ctx.send("The `hint` provided is present in the grid. `/rules` for more info", ephemeral=True)



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
        game = await GAME_LIST.get_game(ctx.channel_id)
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
            await GAME_LIST.delete_game(game.channel_id)

    except GameNotFound:
        await ctx.send("No game created. Use `/create` to create a game !", ephemeral=True)
    except GameNotStarted:
        await ctx.send("The game did not start", ephemeral=True)
    except NotInGame:
        await ctx.send("You are not in the game", ephemeral=True)
    except NotYourRole:
         await ctx.send("You are a spy you can not use this command !", ephemeral=True)
    except NotYourTurn as e:
        await ctx.send(f"{e}", ephemeral=True)
    except WordNotInGrid:
        await ctx.send("The the provided is not in the grid", ephemeral=True)

@bot.command()
@bot.component("skip_button_id")
async def skip(ctx: interactions.CommandContext):
    """End the player turn if at least one word is proposed"""
    try:
        game = await GAME_LIST.get_game(ctx.channel_id)
        await game.skip(ctx.user)
        await ctx.send(f"{ctx.user.username} skipped their turn...\
                       \n\
                       \n{state_message(game)}", components=state_component(game))
    except GameNotFound:
        await ctx.send("No game created. Use `/create` to create a game !", ephemeral=True)
    except GameNotStarted:
        await ctx.send("The game did not start", ephemeral=True)
    except NotInGame:
        await ctx.send("You are not in the game", ephemeral=True)
    except NotYourRole:
         await ctx.send("You are a spy you can not use this command !", ephemeral=True)
    except NotYourTurn as e:
        await ctx.send(f"{e}", ephemeral=True)
    except NoWordFound:
        await ctx.send("You must guess at least one word in the grid", ephemeral=True)
    


bot.start()