import discord
import json
import os.path
from discord.ext import commands


class Delete(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 前綴指令
    @commands.command()
    async def delete(self, ctx: commands.Context, quest_parameter: str):
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
                    for course_url in course['url']:
                        if course_url == "https://cos3s.ntnu.edu.tw/AasEnrollStudent/CourseQueryCtrl?" + quest_parameter:
                            course['url'].remove(course_url)
                            determined = True
                            break

            if not determined:
                await ctx.send("Hi, {0.author.name}. 查無可刪除的資料，請使用`!check`確認後重試。".format(ctx))
            else:
                with open(file_path, 'w', encoding='utf-8') as ff:
                    json.dump(data, ff, ensure_ascii=False, indent=4)
                await ctx.send("Hi, {0.author.name}. 您已刪除一筆課程。可以使用`!check`指令查詢目前所剩項目。".format(ctx))

    # 關鍵字觸發
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return


async def setup(bot: commands.Bot):
    await bot.add_cog(Delete(bot))
