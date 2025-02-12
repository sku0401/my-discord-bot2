import discord
from discord import app_commands
import random
import os
import asyncio
import aiohttp
from aiohttp import web
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# Botの設定
intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# ユーザーの口調状態管理
user_styles = {}

# ランダムな会話リスト
talk_responses = [
    "こんにちは！今日はどうだった？",
    "元気だった？最近何か面白いことあった？",
    "お疲れ様～！今日はどんな感じだったかな？",
    "やっほ！最近どうしてたの～？",
    "こんにちはっ！今日も元気にいこうね！"
]

# ボット起動時
@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ {bot.user} としてログインしました！")

# メスガキ口調変更コマンド
@tree.command(name="mesugaki", description="メスガキ口調になる")
async def mesugaki(interaction: discord.Interaction):
    user_styles[interaction.user.id] = "mesugaki"
    await interaction.response.send_message(f"{interaction.user.name} はメスガキ口調になったにゃ！")

# 口調リセットコマンド
@tree.command(name="reset", description="口調を元に戻す")
async def reset(interaction: discord.Interaction):
    if interaction.user.id in user_styles:
        del user_styles[interaction.user.id]
    await interaction.response.send_message(f"{interaction.user.name} の口調が元に戻ったにゃん！")

# ランダムな会話生成
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id
    response = random.choice(talk_responses)

    # メスガキ口調対応
    if user_id in user_styles and user_styles[user_id] == "mesugaki":
        response = "うるさいにゃん！こっち来いよ、早くにゃ！"

    await message.channel.send(response)

# ダイスロールコマンド
@tree.command(name="dice", description="n個のm面のダイスを振る (例: /dice 2d6)")
async def dice(interaction: discord.Interaction, dice_input: str):
    try:
        num_dice, dice_sides = map(int, dice_input.lower().split('d'))
        rolls = [random.randint(1, dice_sides) for _ in range(num_dice)]
        total = sum(rolls)
        roll_result = ', '.join(map(str, rolls))
        await interaction.response.send_message(f"🎲 ロール結果: {roll_result} (合計: {total})")
    except ValueError:
        await interaction.response.send_message("⚠️ 入力形式が違うみたい。「2d6」みたいに入力してね！")

# じゃんけんコマンド
@tree.command(name="janken", description="じゃんけんをする")
async def janken(interaction: discord.Interaction):
    hands = ["グー", "チョキ", "パー"]
    bot_hand = random.choice(hands)

    results = {
        ("グー", "チョキ"): "あなたの勝ち！🎉",
        ("チョキ", "パー"): "あなたの勝ち！🎉",
        ("パー", "グー"): "あなたの勝ち！🎉",
        ("チョキ", "グー"): "あなたの負け…😢",
        ("パー", "チョキ"): "あなたの負け…😢",
        ("グー", "パー"): "あなたの負け…😢"
    }

    result = results.get((interaction.user.name, bot_hand), "あいこだね！😊")
    await interaction.response.send_message(f"あなた: {interaction.user.name} - ボット: {bot_hand}\n結果: {result}")

# ヘルプコマンド
@tree.command(name="help", description="コマンド一覧を表示")
async def help_command(interaction: discord.Interaction):
    help_text = """
    **コマンド一覧**
    - `/dice <n>d<m>`: n個のm面のダイスを振る (例: `/dice 2d6`)
    - `/janken`: じゃんけんをする
    - `/mesugaki`: メスガキ口調になる
    - `/reset`: 口調を元に戻す
    - `/help`: コマンド一覧を表示
    """
    await interaction.response.send_message(help_text)

# Render用のポート設定（健康チェック用Webサーバー）
PORT = int(os.getenv("PORT", 8080))

async def handle(request):
    return web.Response(text="Bot is running")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

# ボット起動
async def main():
    await start_web_server()
    await bot.start(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    asyncio.run(main())
