import interactions
import os
from dotenv import load_dotenv
from GameList import GameList
from Language import Language
from ColorCard import ColorCard
from CodeGameExceptions import *
from Game import Game, State
import CodeNamesButton as CNButton
import CodeNamesModal as CNTextInput
from CodeNamesButton import CodeNamesButton
from Creator import Creator
import io
from word_list import write_list_file
import Translator

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
GUILD_ID = os.getenv('GUILD_ID')
GUILD_ID = int(GUILD_ID) if GUILD_ID != None and GUILD_ID.isnumeric() else None

bot = interactions.Client(token=BOT_TOKEN, default_scope=GUILD_ID)#, presence=interactions.ClientPresence(status=interactions.StatusType.INVISIBLE))

GAME_LIST = GameList()



@bot.user_command(name="User Command")
async def test(ctx: interactions.CommandContext):
    print(ctx.channel_id)
    if not isinstance(ctx.target, interactions.Member):
        await ctx.send(f"You have applied a command onto an unknown user!")
        return
    if ctx.target.user is None:
        await ctx.send(f"You have applied a command onto None!")
        return
    
    await ctx.send(f"You have applied a command onto user {ctx.target.user.username}!")



# ================================
# ============= MODAL ============
# ================================




async def send_modal(ctx:interactions.CommandContext, game:Game):
    modal = CNTextInput.state_modal(game)
    if modal is None:
        return await ctx.send(Translator.get_error_message(game.language))
    await ctx.popup(modal)

@bot.modal("spy_modal")
async def spy_modal(ctx:interactions.CommandContext, hint: str, nb_try:str):
    try:
        if(not nb_try.isnumeric()):
            raise WrongHintNumberGiven(language=Language.get_discord_equivalent(ctx.locale))
        await suggest(ctx=ctx, hint=hint, number_of_try=int(nb_try))
    except WrongHintNumberGiven as e:
        await ctx.send(e.message, ephemeral=True)
    # await ctx.send(f"ESPION: {hint}, {nb_try}", ephemeral=True)

@bot.modal("player_modal")
async def player_modal(ctx:interactions.CommandContext, response: str):
    if(response.isnumeric()):
        await guess_by_func(ctx=ctx, card_id=int(response))
    else:
        await guess_by_func(ctx=ctx, word=response)



@bot.command()
@bot.component(CodeNamesButton.DISPLAY_GRID_BUTTON.value)
async def display(ctx: interactions.CommandContext):
    """Display the grid depending on your role"""
    try:
        game = await GAME_LIST.get_game(str(ctx.channel_id), language=Language.get_discord_equivalent(ctx.locale))
        image = interactions.File(game.get_user_image_path(ctx.user))
        await ctx.send(files=image, ephemeral=True)
    except (GameNotFound, GameNotStarted, NotInGame, FileNotFoundError) as e:
        if isinstance(e, FileNotFoundError):
            message = Translator.get_error_message(language=Language.get_discord_equivalent(ctx.locale))
        else :
            message = e.message
        await ctx.send(message, ephemeral=True)

@bot.component(CodeNamesButton.SPY_BUTTON.value)
async def spy(ctx: interactions.ComponentContext):
    try:
        game = await GAME_LIST.get_game(str(ctx.channel_id), language=Language.get_discord_equivalent(ctx.locale))
        game.invert_can_be_spy(user=ctx.user)

        if ctx.message is None:
            await ctx.send(Translator.get_error_message(language=game.language))
            return
        
        await ctx.message.edit(
            content=Translator.get_create_message(game), 
            components=CNButton.state_component(game),
            allowed_mentions=interactions.AllowedMentions(users=game.get_all_pretenders_id())
        )
        await ctx.edit(ctx.message.content)

    except (GameNotFound, NotInGame, GameAlreadyStarted) as e:
        await ctx.send(e.message, ephemeral=True)


@bot.command() # type: ignore
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
@interactions.option(
    description="Chose the number of team of the game",
    type=interactions.OptionType.INTEGER,
    name="nb_teams",
    required=True,
    choices=[
        interactions.Choice(name="1", value=1),
        interactions.Choice(name="2", value=2),
        interactions.Choice(name="3", value=3),
        interactions.Choice(name="4", value=4)
    ] 
)
@interactions.option(
    description="Select True if you want to play with the default word list of the selected language, else False",
    name="default_word_list",
    type=interactions.OptionType.BOOLEAN,
    required=False
)
@interactions.option(
    description="Select True if you want to play with your server word list, else False",
    name="server_word_list",
    type=interactions.OptionType.BOOLEAN,
    required=False
)
async def create(ctx: interactions.CommandContext, language:str, nb_teams:int, default_word_list:bool=True, server_word_list:bool=False):
    """Create a game of Code Names"""
    lang:Language = Language.get_by_string(language_string=language)
    try:
        creator = Creator(language=lang, channel_id=str(ctx.channel_id), creator_id=str(ctx.user.id), guild_id=str(ctx.guild_id))
        game:Game = await GAME_LIST.create_game(
            creator=creator, 
            nb_teams=nb_teams, 
            default_word_list=default_word_list, 
            server_word_list=server_word_list)
        await ctx.send(
            content=Translator.get_create_message(game), 
            components=CNButton.state_component(game),
            allowed_mentions=interactions.AllowedMentions(users=game.get_all_pretenders_id())
        )
    except (GameInChannelAlreadyCreated, WordListFileNotFound, NotEnoughWordsInFile) as e:
        await ctx.send(e.message, ephemeral=True)



@bot.command()
async def delete(ctx: interactions.CommandContext):
    """Delete the current channel game of Code Names"""
    try:
        language:Language = Language.get_discord_equivalent(ctx.locale)
        await GAME_LIST.delete_game(channel_id=str(ctx.channel_id), language=language)
        await ctx.send(Translator.get_deleted_message(ctx.user.username, language=language))
    except GameNotFound as e:
        await ctx.send(e.message, ephemeral=True)


async def join_team(
        ctx: interactions.ComponentContext | interactions.CommandContext, 
        team:str, 
        spy:bool | None,
        message:interactions.Message | None =None):
    color = ColorCard.get_by_string(color_string=team)
    try:
        game:Game = await GAME_LIST.get_game(str(ctx.channel_id), language=Language.get_discord_equivalent(ctx.locale))
        await game.join(ctx.user, team_color=color, can_be_spy=spy)
        if message is None:
            await ctx.send(Translator.get_joined_message(ctx.user.username, color, language=game.language))
            return
        await message.edit(
            content=Translator.get_create_message(game), 
            components=CNButton.state_component(game), 
            allowed_mentions=interactions.AllowedMentions(users=game.get_all_pretenders_id())
        )

        # avoid "Error with interaction" message in discord
        if ctx.message is None:
            await ctx.send(Translator.get_error_message(language=game.language))
            return
        await ctx.edit(ctx.message.content)

    except (GameNotFound, GameAlreadyStarted, TeamNotAvailable) as e:
        await ctx.send(e.message, ephemeral=True)



@bot.command() # type: ignore
@interactions.option(
    description="Chose your team !",
    type=interactions.OptionType.STRING,
    name="team",
    required=True,
    choices=[
        interactions.Choice(name=ColorCard.BLUE.value, value=ColorCard.BLUE.value),
        interactions.Choice(name=ColorCard.RED.value, value=ColorCard.RED.value),
        interactions.Choice(name=ColorCard.GREEN.value, value=ColorCard.GREEN.value),
        interactions.Choice(name=ColorCard.YELLOW.value, value=ColorCard.YELLOW.value)
    ] 
)
@interactions.option(
    description="True if you want to be chose to be the spy, else False",
    name="spy",
    type=interactions.OptionType.BOOLEAN,
    required=False
)
async def join(ctx: interactions.CommandContext, team:str, spy:bool=False):
    """Join a game of Code Names"""
    await join_team(ctx, team, spy=spy)



@bot.component(CodeNamesButton.RED_JOIN_BUTTON.value)
async def on_login_red_click(ctx:interactions.ComponentContext):
    await join_team(ctx, team=ColorCard.RED.value, spy=None, message=ctx.message)


@bot.component(CodeNamesButton.BLUE_JOIN_BUTTON.value)
async def on_login_blue_click(ctx:interactions.CommandContext):
    await join_team(ctx, team=ColorCard.BLUE.value, spy=None, message=ctx.message)


@bot.component(CodeNamesButton.GREEN_JOIN_BUTTON.value)
async def on_login_green_click(ctx:interactions.CommandContext):
    await join_team(ctx, team=ColorCard.GREEN.value, spy=None, message=ctx.message)


@bot.component(CodeNamesButton.YELLOW_JOIN_BUTTON.value)
async def on_login_yellow_click(ctx:interactions.CommandContext):
    await join_team(ctx, team=ColorCard.YELLOW.value, spy=None, message=ctx.message)

@bot.component(CodeNamesButton.SPY_INTERACTION_BUTTON.value)
@bot.component(CodeNamesButton.PLAYER_INTERACTION_BUTTON.value)
async def on_base_action_click(ctx:interactions.CommandContext):
    try:
        game:Game = await GAME_LIST.get_game(str(ctx.channel_id), language=Language.get_discord_equivalent(ctx.locale))
        await send_modal(ctx, game)

    except (GameNotFound) as e:
        await ctx.send(e.message, ephemeral=True)



@bot.command()
@bot.component(CodeNamesButton.LEAVE_BUTTON.value)
async def leave(ctx: interactions.CommandContext):
    """leave a game that did not start"""
    try:
        game:Game = await GAME_LIST.get_game(str(ctx.channel_id), language=Language.get_discord_equivalent(ctx.locale))
        await game.leave(ctx.user)
        if(ctx.message != None):
            await ctx.message.edit(
                content=Translator.get_create_message(game), 
                components=CNButton.state_component(game),
                allowed_mentions=interactions.AllowedMentions(users=game.get_all_pretenders_id())
            )
            await ctx.send(Translator.get_global_left_message(language=game.language), ephemeral=True)
        else:
            await ctx.send(Translator.get_left_message(ctx.user.username, language=game.language))
    except (GameNotFound, NotInGame, GameAlreadyStarted) as e:
        await ctx.send(e.message, ephemeral=True)



@bot.command()
@bot.component(CodeNamesButton.START_BUTTON.value)
async def start(ctx: interactions.CommandContext):
    """Start the game of Code Names"""
    try:
        game = await GAME_LIST.get_game(str(ctx.channel_id), language=Language.get_discord_equivalent(ctx.locale))
        await game.start(str(ctx.user.id))
        image = interactions.File(game.get_image_path())
        await ctx.send(f"\n{Translator.starting_message(game)}\
                       \n\
                       \n{Translator.state_message(game)}",
                    components=CNButton.state_component(game),
                    files=image,
                    allowed_mentions=interactions.AllowedMentions(users=[int(game.spies[game.color_state].user.id)])
        )
        # await ctx.send(state_message(game), components=state_component(game))
    except (GameNotFound, NotGameCreator, GameAlreadyStarted, NotEnoughPlayerInTeam) as e:
        await ctx.send(e.message, ephemeral=True)



@bot.command() # type: ignore
@interactions.option(description="A hint that will help your teammates to guess the words of your color. Use `/rules` for more info")
@interactions.option(description="The number of tries your teammates will have to guess the words")
async def suggest(ctx: interactions.CommandContext, hint:str, number_of_try:int):
    """Suggest a hint to help your team to guess words. Provide also a number of try"""
    try:
        game = await GAME_LIST.get_game(str(ctx.channel_id), language=Language.get_discord_equivalent(ctx.locale))
        await game.suggest(ctx.user, hint, number_of_try)

        await ctx.send(Translator.state_message(game), components=CNButton.state_component(game))

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


async def guess_by_func(ctx: interactions.CommandContext, word:str | None = None, card_id: int | None = None):
    try:
        game = await GAME_LIST.get_game(str(ctx.channel_id), language=Language.get_discord_equivalent(ctx.locale))
        if word == None and card_id != None:
            (card_color, word_found) = await game.guess_by_card_id(ctx.user, card_id)
        elif word != None and card_id == None:
            (card_color, word_found) = await game.guess_by_word(ctx.user, word)
        else:
            # can't happen
            await ctx.send(Translator.get_error_message(language=game.language))
            return
        image = interactions.File(game.get_image_path(isSpy=(game.state== State.WIN)))
        await ctx.send(f"{Translator.get_revealed_word_message(word_found, card_color, language=game.language)}\
                       \n\
                       {Translator.remaining_words_messages(game)}\
                       \n\
                       \n{Translator.state_message(game)}",
                       files=image, 
                       components=CNButton.state_component(game)
        )
        if game.state == State.WIN:
            await GAME_LIST.delete_game(game.channel_id, language=Language.get_discord_equivalent(ctx.locale))

    except (GameNotFound, GameNotStarted, NotInGame, NotYourRole, NotYourTurn, WordNotInGrid, WrongCardIdNumberGiven) as e:
        await ctx.send(e.message, ephemeral=True)

@bot.command()
@bot.component(CodeNamesButton.SKIP_BUTTON.value)
async def skip(ctx: interactions.CommandContext):
    """End the player turn if at least one word is proposed"""
    try:
        game = await GAME_LIST.get_game(str(ctx.channel_id), language=Language.get_discord_equivalent(ctx.locale))
        await game.skip(ctx.user)
        await ctx.send(f"{Translator.get_skipped_message(player_name=ctx.user.username, language=game.language)}\
                       \n\
                       \n{Translator.state_message(game)}", components=CNButton.state_component(game))
    except (GameNotFound, GameNotStarted, NotInGame, NotYourRole, NotYourTurn, NoWordGuessed) as e:
        await ctx.send(e.message, ephemeral=True)


@bot.command() # type: ignore
@interactions.option(
    description=".txt with alphanumerical or `-` characters. 1 word (<12 char) per line, 1000 words max, no duplicate",
    type=interactions.OptionType.ATTACHMENT,
    name="file"
)
async def upload(ctx: interactions.CommandContext, file: interactions.Attachment):
    """Send a list of word in a `.txt` file"""
    guild = await ctx.get_guild()
    if not file.filename.endswith(".txt"):
        return await ctx.send("The file must be a tkt file")
    if file.size > 15000:
        print(file.size)
        size_kB = str(file.size/1000)
        return await ctx.send(f"The file is too large. Received: {size_kB[:size_kB.find('.')+2]}kB, max: 15kB", ephemeral=True)
    downloaded_file = await file.download()
    wrapper = io.TextIOWrapper(downloaded_file, encoding='utf-8')
    write_list_file(wrapper, max_word=1000, max_length_word=11, guild_id=str(guild.id))
    return await ctx.send("File added")


bot.start()