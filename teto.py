import datetime
import re
import asyncio
import logging

import discord
from discord.ext import commands, tasks

import functions

class Teto(commands.Cog):
    """Commands for the community!"""
    def __init__(self, bot):
        self.bot = bot
        self.queue = ["tetoTerritory.mp3","test2.mp3","test3.mp3"] # this only works on one guild (oh well)
        self.queueIndex = 0

    @commands.group(help="teto", brief="<:TetoAngery:772166738301026355> ")
    async def teto(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("HI IM TETO (ASK ME WHAT DEEZ IS)")

    @teto.command(name="slur",help="slur", brief="<:TetoAngery:772166738301026355> ")
    async def teto_slur(self,ctx):
        await ctx.send("I WILL LIST MY TOP 10 SLURS:\n\ndeez")

    @teto.command(name="among")
    async def among(self,ctx):
        await ctx.send("US! I LOVE AMONG  US!")

    @commands.Cog.listener()
    async def on_message(self,message):
        if (re.search(r"what.+?deez",message.content.lower()) or "deez?" in message.content.lower()) and message.author != message.guild.me:
            await message.channel.send("DEEZ NUTS LOL") 
    
    @teto.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel=None):
        """Joins a voice channel"""
        if not channel:
            if ctx.author.voice:
                channel = ctx.author.voice.channel
            else:
                return await ctx.send("You are not in a voice channel.")
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)
        await channel.connect()
        self.connected_guild = ctx.guild
        self.song_end(None)

    @teto.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @teto.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""
        await ctx.voice_client.disconnect()
        self.queueIndex = -1

    def song_end(self,error):
        if error:
            logging.warning("Uhh there was an error.")
            logging.warning(error)
        self.queueIndex += 1
        if self.queueIndex == len(self.queue):
            self.queueIndex = 0
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio("cogs/YayaBot-Cogs/audio/"+self.queue[self.queueIndex]))
        try:
            self.connected_guild.voice_client.play(source, after=self.song_end)
        except:
            pass

    def cog_unload(self):
        self.queue = []
        self.connected_guild.voice_client.stop()

def setup(bot):
    bot.add_cog(Teto(bot))
