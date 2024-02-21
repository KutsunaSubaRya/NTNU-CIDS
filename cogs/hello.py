import discord
from discord.ext import commands


class Hello(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 前綴指令
    @commands.command()
    async def hello(self, ctx: commands.Context):
        await ctx.send("Hello, world! {0.author.mention}".format(ctx))

    # 關鍵字觸發
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        if "Hello" in message.content:
            await message.channel.send("Bot says: Hello, world! : )")


async def setup(bot: commands.Bot):
    await bot.add_cog(Hello(bot))
