import discord
import os
from dotenv import load_dotenv
from extract_phrase import extract_phrase
from special_reply import init,special_reply_exact,special_reply_contains,special_reply_endswith,special_reply_ordered,mention_reply

from discord.ext import commands
from discord.ext import tasks
import asyncio
import random
import json
from pathlib import Path


from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
#初期設定
#==============================
REPLY_PROBABILITY = 0.1
#らいな雑談、くらうどーむ雑談、らいな雑談2、創作雑談、くらうどーむメモ、一般
ACTIVE_CHANNELS = {1456597613926154452,1468960224730943560,1526572399833911296,1438885241170428068,1533682775448883260,1534055479049981974}
#==============================



load_dotenv()
api_key = os.getenv("API_KEY")

bot_status = "awake"

# インテントの生成
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# 時刻の設定
JST = ZoneInfo("Asia/Tokyo")
# 特定メッセージを送るチャンネルID
TARGET_CHANNEL_IDS = [
    123456789012345678,
    234567890123456789,
    345678901234567890,
]
DAILY_PROBABILITY = 0.15
NEBOU_PROBABILITY = 0.1
HAYAI_PROBABILITY = 0.1


# 決まった時間の固定メッセージ
# 時間も、基準の時間から±30分ぐらい前後してランダムに選びたい
async def daily_message():
    while True:
        now = datetime.now(JST)
        nebou = False
        hayai = False

        # 今日の07:00を基準にする
        target = now.replace(
            hour=7,
            minute=0,
            second=0,
            microsecond=0
        )

        # ±30分をランダムにする
        offset = random.randint(-30, 30)
        target += timedelta(minutes=offset)

        # 確率でやばい時間にしよう
        if random.random() <= NEBOU_PROBABILITY:
            offset = random.randint(180, 210)
            target += timedelta(minutes=offset)
            nebou = True
        elif random.random() <= HAYAI_PROBABILITY:
            offset = random.randint(-210, -180)
            target += timedelta(minutes=offset)
            hayai = True

        # すでに実行時刻を過ぎていたら明日の07:00を基準にする
        if target <= now:
            target += timedelta(days=1)

        # 次回実行まで待つ
        wait_seconds = (target - now).total_seconds()

        print(
            f"次回の定期メッセージ: "
            f"{target.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        await asyncio.sleep(wait_seconds)

        # チャンネルをランダムに1つ選択
        channel_id = random.choice(TARGET_CHANNEL_IDS)
        channel = bot.get_channel(channel_id)

        if channel is None:
            print(f"チャンネルが見つかりません: {channel_id}")
            continue
        if random.random() >= DAILY_PROBABILITY:
            continue
        phrase = random.choice(
            ["おはつぐ～！！","おはつぐ！","おはつぐ☀️"]
        )
        if nebou:
            phrase += "（大寝坊して無事終了）"
        elif hayai:
            phrase += "（ありえない時間に目が覚めすぎている）"
        await channel.send(phrase)

# メッセージを受信した時に呼ばれる
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if bot_status == "sleep":
        return
    


    init(message)
    if bot.user in message.mentions:
        await mention_reply(message)

    if message.channel.id not in ACTIVE_CHANNELS:
        if random.random() >= REPLY_PROBABILITY:
            return

    if await special_reply_exact(message):
        return
    if await special_reply_contains(message):
        return
    if await special_reply_endswith(message):
        return
    if await special_reply_ordered(message):
        return


        
    phrase = extract_phrase(message.content)
    if phrase:
        await message.reply(
            f"僕は...僕は...{phrase}って言ったじゃないか！！！",
            mention_author=False
        )
    await bot.process_commands(message)

@bot.tree.command(
    name="sleep",
    description="30分寝ます"
)
async def sleep(interaction: discord.Interaction):

    global bot_status

    bot_status = "sleep"

    await interaction.response.send_message(
        "30分だけ寝ますおやすみ！！！！！"
    )

    await asyncio.sleep(1800)

    bot_status = "awake"



# discordと接続した時に呼ばれる
@bot.event
async def on_ready():
    await bot.tree.sync()

    if daily_message_task is None or daily_message_task.done():
        daily_message_task = asyncio.create_task(
            daily_message()
        )
        
    print(f"ログインしました: {bot.user}")



# クライアントの実行
bot.run(api_key)