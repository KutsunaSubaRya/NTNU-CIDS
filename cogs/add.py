import discord
import json
import os.path
from discord.ext import commands


class Add(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 前綴指令
    @commands.command()
    async def add(self, ctx: commands.Context, quest_parameter: str):
        data = []
        file_path = os.path.dirname(__file__) + '/../course_list.json'
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
            determined: bool = False
            for course in data:
                if course['name'] == ctx.author.mention:
                    course['url'].append(
                        "https://cos3s.ntnu.edu.tw/AasEnrollStudent/CourseQueryCtrl?" + quest_parameter)
                    determined = True
                    break

            if not determined:
                data.append({'name': ctx.author.mention,
                             'url': ["https://cos3s.ntnu.edu.tw/AasEnrollStudent/CourseQueryCtrl?" + quest_parameter]})
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        await ctx.send("Hi, {0.author.name}. 您已新增一筆課程。可以使用`!check`指令查詢已加入的項目，若有空位將立即通知您。".format(ctx))

    # 關鍵字觸發
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return


async def setup(bot: commands.Bot):
    await bot.add_cog(Add(bot))
