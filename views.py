from typing import List, Optional
import random
import logging

import discord
from discord.ext import commands

import functions

try:
    assert discord.__version__[0] == "2"
except AssertionError:
    logging.error("The views cog was made for Discord.py 2.0, currently you can install this using 'pip install git+https://github.com/Rapptz/discord.py'. It's not release ready yet, this is just a test.")
    raise

# Defines a custom button that contains the logic of the game.
# The ['TicTacToe'] bit is for type hinting purposes to tell your IDE or linter
# what the type of `self.view` is. It is not required.
class TicTacToeButton(discord.ui.Button['TicTacToe']):
    def __init__(self, x: int, y: int):
        # A label is required, but we don't need one so a zero-width space is used
        # The row parameter tells the View which row to place the button under.
        # A View can only contain up to 5 rows -- each row can only have 5 buttons.
        # Since a Tic Tac Toe grid is 3x3 that means we have 3 rows and 3 columns.
        super().__init__(style=discord.ButtonStyle.secondary, label='‫', row=y)
        self.x = x
        self.y = y

    # This function is called whenever this particular button is pressed
    # This is part of the "meat" of the game logic
    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: TicTacToe = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return

        if view.current_player == view.X and interaction.user == view.playerOne:
            self.style = discord.ButtonStyle.danger
            self.label = 'X'
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            content = f"It is now {view.playerTwo.mention}'s (O) turn"
        elif view.current_player == view.O and interaction.user == view.playerTwo:
            self.style = discord.ButtonStyle.success
            self.label = 'O'
            self.disabled = True
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            content = f"It is now {view.playerOne.mention}'s (X) turn"
        else:
            return

        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = f'{view.playerOne.mention} (X) won!'
            elif winner == view.O:
                content = f'{view.playerTwo.mention} (O) won!'
            else:
                content = "It's a tie!"

            for child in view.children:
                child.disabled = True

            view.stop()

        await interaction.response.edit_message(content=content, view=view)


class TicTacToe(discord.ui.View):
    children: List[TicTacToeButton]
    X = -1
    O = 1
    Tie = 2

    def __init__(self,playerOne,playerTwo):
        super().__init__()
        self.current_player = self.X
        self.playerOne = playerOne
        self.playerTwo = playerTwo
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))

    def check_board_winner(self):
        for across in self.board:
            value = sum(across)
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        for line in range(3):
            value = self.board[0][line] + self.board[1][line] + self.board[2][line]
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        if all(i != 0 for row in self.board for i in row):
            return self.Tie

        return None

class PollButton(discord.ui.Button['Poll']):
    def __init__(self,option):
        super().__init__(label=option + ": 0",style=discord.ButtonStyle.green)
        self.option = option

    async def update_label(self):
        self.label = self.option + ": " + str(len([i for i in self.view.votes.values() if i == self.option]))

    async def callback(self, interaction: discord.Interaction):
        self.view.votes[interaction.user.id] = self.option
        await self.view.check_buttons()
        await interaction.response.edit_message(content=f"Poll! Ends {self.timeoutS}.\nVote Below:",view=self.view)

class Poll(discord.ui.View):
    message: discord.Message

    def __init__(self,duration,items,timeoutS):
        super().__init__(timeout=duration)
        self.votes = {} # userid: option
        self.timeoutS = timeoutS
        for item in items:
            self.add_item(PollButton(item))

    async def check_buttons(self):
        for child in self.children:
            await child.update_label()

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit("Poll Over!",view=self)

class Rated(discord.ui.View):
    def __init__(self,values,average):
        super().__init__(timeout=1)
        values = [str(i) for i in values]
        self.add_item(discord.ui.Button(label="This Rating Has Ended:",style=discord.ButtonStyle.green,row=0))
        self.add_item(discord.ui.Button(label=f"Final Ratings: {', '.join(values)}",style=discord.ButtonStyle.primary,row=1))
        self.add_item(discord.ui.Button(label=f"Final Average: {average}",style=discord.ButtonStyle.primary,row=1))

class RatingButton(discord.ui.Button['Rating']):
    def __init__(self, rating):
        row = int(rating/4)+1 if isinstance(rating,int) else 3
        super().__init__(style=discord.ButtonStyle.secondary, label=str(rating),row=row)
        self.rating = rating

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view = self.view
        if isinstance(self.rating,int):
            view.ratings[interaction.user.id] = self.rating
        else:
            view.ratings.pop(interaction.user.id)
        [child for child in view.children if child.custom_id == "ratingList"][0].label = 'Current Ratings: ' + ', '.join([str(i) for i in view.ratings.values()])
        if view.ratings:
            average = sum(view.ratings.values())/len(view.ratings.values())
            average = int(average) if average % 1 == 0 else average
        else:
            average = ""
        [child for child in view.children if child.custom_id == "ratingAverage"][0].label = 'Average Rating: ' + str(average)
        await interaction.response.edit_message(content=view.msg, view=view)

class Rating(discord.ui.View):
    message: discord.Message

    def __init__(self,msg: str,timeout: Optional[int]):
        super().__init__(timeout=timeout)
        self.msg = msg
        self.ratings = {}
        _=[self.add_item(RatingButton(i)) for i in range(11)]
        self.add_item(RatingButton("Clear"))

    async def on_timeout(self):
        if self.ratings:
            average = sum(self.ratings.values())/len(self.ratings.values())
            average = int(average) if average % 1 == 0 else average
        else:
            average = ""
        newview = Rated(self.ratings.values(),average)
        await self.message.edit("This rating has now ended\n\n"+self.msg,view=newview)

    @discord.ui.button(label="Current Ratings: ", style=discord.ButtonStyle.primary, custom_id="ratingList", row=0)
    async def current(self,button: discord.ui.Button, interaction: discord.Interaction):
        return

    @discord.ui.button(label="Average Rating: ", style=discord.ButtonStyle.primary, custom_id="ratingAverage", row=0)
    async def average(self,button: discord.ui.Button, interaction: discord.Interaction):
        return

class Views(commands.Cog):
    """Commands that use the - as of yet - unreleased view feature coming in discord.py 2.0, these may be implemented in actual YayaBot once discord.py 2.0 is released."""
    def __init__(self,bot):
        self.bot = bot

    @commands.command(help="Create a Poll! Duration can be seconds ('20s'), minutes ('5m'), hours ('10h') or days ('1d')",brief="☑️ ")
    async def poll(self,ctx,duration: str,*,items: str):
        duration = functions.timeconverters().secondsconverter(int(duration[:-1]),duration[-1])
        items = items.split(";")
        timeoutS = functions.DiscordTimestamp(duration,relative=True).relative
        ratingview = Poll(duration,items,timeoutS)
        message = await ctx.send(f"Poll! Ends {timeoutS}.\nVote Below:",view=ratingview)
        ratingview.message = message

    @commands.command()
    async def rate(self,ctx,timeout: Optional[int]=None,*,work):
        if ctx.message.attachments:
            work += " " + str(ctx.message.attachments[0].url)
        msg = f"We are rating: {work}\nChoose your rating with the buttons below."
        if timeout:
            msg += f"\nThis rating will end after {timeout} seconds."
        ratingview = Rating(msg,timeout)
        message = await ctx.send(msg,view=ratingview)
        ratingview.message = message

    @commands.command()
    async def tic(self,ctx: commands.Context,playerTwo: discord.Member):
        """Starts a tic-tac-toe game with playerTwo."""
        if random.randint(0,1) == 1:
            playerOne = playerTwo
            playerTwo = ctx.author
        else:
            playerOne = ctx.author
        await ctx.send(f'Tic Tac Toe: {playerOne.mention} (X) goes first', view=TicTacToe(playerOne,playerTwo))


def setup(bot):
    bot.add_cog(Views(bot))
