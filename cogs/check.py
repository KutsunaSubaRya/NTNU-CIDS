import discord
import json
import os.path
from discord.ext import commands


class Check(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 前綴指令
    @commands.command()
    async def check(self, ctx: commands.Context):
        data = []
        resdata = ""
        file_path = os.path.dirname(__file__) + '/../course_list.json'
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
            determined: bool = False
            for course in data:
                if course['name'] == ctx.author.mention:
                    for course_url in course['url']:
                        resdata += course_url + "\n"
                    determined = True
                    break

            if not determined:
                await ctx.send("Hi, {0.author.name}. 查無資料。".format(ctx))
        await ctx.send(
            "Hi, {0.author.name}. 您已新增的課程如下： \n如欲點擊下方連結確認開課序號，請先至 https://cos3s.ntnu.edu.tw/AasEnrollStudent/LoginCheckCtrl?language=TW 登入後，再點擊下方連結。\n{1}".format(
                ctx, resdata))

    # 關鍵字觸發
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return


async def setup(bot: commands.Bot):
    await bot.add_cog(Check(bot))
