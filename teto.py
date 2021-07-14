
import discord
from discord.ext import commands


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

    @commands.Cog.listener()
    async def on_message(self,message):
        if "what is deez" in message.content:
            await message.channel.send("DEEZ NUTS LOL")

def setup(bot):
    bot.add_cog(Teto(bot))
