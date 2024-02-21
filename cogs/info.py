import discord
from discord.ext import commands


class Info(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 前綴指令
    @commands.command()
    async def info(self, ctx: commands.Context):
        await ctx.send("Hi, 很高興可以幫助您，請前往下方連結查看完整指令說明與操作指引：\n https://hackmd.io/@SubaRya/rkup50Gh6")

    # 關鍵字觸發
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return


async def setup(bot: commands.Bot):
    await bot.add_cog(Info(bot))
