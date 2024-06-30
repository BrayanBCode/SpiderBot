import discord
from discord.ext import commands
from discord import app_commands
from colorama import Fore
class loop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{Fore.GREEN}[Slash Command] loop cargado.")

    @app_commands.command(name="loop", description="Reproduce una canción")
    async def loop(self, interaction: discord.Interaction):
        await interaction.response.send_message("Sin implementar.")

async def setup(bot):
    await bot.add_cog(loop(bot))