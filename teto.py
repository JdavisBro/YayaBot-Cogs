import datetime
import re

import discord
from discord.ext import commands

import functions

class Teto(commands.Cog):
    """Commands for the community!"""
    def __init__(self, bot):
        self.bot = bot

    @commands.group(help="teto", brief="<:TetoAngery:772166738301026355> ")
    async def teto(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("HI IM TETO (ASK ME WHAT DEEZ IS)")

    @teto.command(name="slur",help="slur", brief="<:TetoAngery:772166738301026355> ")
    async def teto_slur(self,ctx):
        await ctx.send("I WILL LIST MY TOP 10 SLURS:\n\ndeez")

    @commands.command(name="test")
    async def timestamps(self,ctx):
        time = functions.DiscordTimestamp(1625037668)
        await ctx.send(f"Times! {time.date}, {time.date_full}, {time.time}, {time.time_full}, {time.date_time}, {time.date_time_full}, {time.relative}.")
        time = functions.DiscordTimestamp(datetime.timedelta(minutes=20),relative=True)
        await ctx.send(f"Times! {time.date}, {time.date_full}, {time.time}, {time.time_full}, {time.date_time}, {time.date_time_full}, {time.relative}.")

    @teto.command(name="among")
    async def among(self,ctx):
        await ctx.send("US! I LOVE AMONG  US!")

    @commands.Cog.listener()
    async def on_message(self,message):
        if (re.search(r"what.+?deez",message.content.lower()) or "deez?" in message.content.lower()) and message.author != message.guild.me:
            await message.channel.send("DEEZ NUTS LOL")

def setup(bot):
    bot.add_cog(Teto(bot))
