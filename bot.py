import discord
from discord.ext import commands
import random
import os
from dotenv import load_dotenv
from flask import Flask
import threading
from collections import defaultdict

# .envファイルから設定を読み込む
load_dotenv()

# FlaskによるWebサーバー (Render対策)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run():
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

t = threading.Thread(target=run, daemon=True)
t.start()

# Botのインスタンス
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ユーザーごとの会話履歴管理 & 状態管理
user_states = defaultdict(lambda: {"conversation": []})
user_styles = {}

# 設定した会話チャンネル
chat_channels = {}

# 会話パターン
talk_responses = [
    "こんにちは！今日はどんな日だった？",
    "元気だった？最近何か面白いことあった？",
    "お疲れ様～！無理しすぎてない？",
    "やっほ！最近どうしてたの？",
    "おなか空いた…ごはんはもう食べた？",
    "ふわぁ…ちょっと眠いかも。",
    "今日はどんな音楽聴いた？",
    "最近ハマってることある？",
    "宿題終わった？それともまだやってない？",
    "ゲームするなら何が好き？",
]

# 語尾変化オプション
nyan_endings = ["にゃん", "だにゃ", "なのにゃ", "にゃー！", "だよにゃ！"]

# 会話履歴を更新
def update_user_state(user_id, message):
    user_states[user_id]["conversation"].append(message)

# 会話履歴から次の返答を生成
def generate_response_from_history(user_id):
    history = user_states[user_id]["conversation"]
    if not history:
        return random.choice(talk_responses)

    last_message = history[-1]
    if "疲れた" in last_message:
        return "お疲れ様～！無理しないでね！"
    elif "元気" in last_message:
        return "えへへ、元気いっぱいだよ～！"
    else:
        return random.choice(talk_responses)

# === スラッシュコマンド ===
@bot.command(name="nyan", help="語尾がにゃん風になる")
async def nyan(ctx):
    user_styles[ctx.author.id] = "nyan"
    await ctx.send(f"{ctx.author.name}の語尾がにゃん風になったにゃん！")

@bot.command(name="reset", help="口調を元に戻す")
async def reset(ctx):
    user_styles.pop(ctx.author.id, None)
    await ctx.send(f"{ctx.author.name}の口調が元に戻ったよ！")

@bot.command(name="setchannel", help="このチャンネルを会話チャンネルに設定する")
async def setchannel(ctx):
    chat_channels[ctx.guild.id] = ctx.channel.id
    await ctx.send("このチャンネルを会話チャンネルに設定したよ！")

@bot.command(name="unsetchannel", help="会話チャンネルの設定を解除する")
async def unsetchannel(ctx):
    if ctx.guild.id in chat_channels:
        del chat_channels[ctx.guild.id]
        await ctx.send("会話チャンネルの設定を解除したよ！")
    else:
        await ctx.send("会話チャンネルはまだ設定されていないよ！")

@bot.command(name="dice", help="n個のm面のダイスを振る (例: 2d6)")
async def dice(ctx, dice_input: str):
    try:
        num_dice, dice_sides = map(int, dice_input.lower().split('d'))
        if num_dice < 1 or dice_sides < 1:
            raise ValueError("正の整数を指定してください！")
        
        rolls = [random.randint(1, dice_sides) for _ in range(num_dice)]
        total = sum(rolls)
        roll_result = ', '.join(map(str, rolls))
        await ctx.send(f"🎲 ロール結果: {roll_result} (合計: {total})")
    
    except ValueError:
        await ctx.send("⚠️ 入力形式が間違ってるよ！「2d6」みたいに入力してね！")

# メッセージイベント: 会話システム
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    guild_id = message.guild.id if message.guild else None
    if guild_id and guild_id in chat_channels and message.channel.id != chat_channels[guild_id]:
        return  # 設定したチャンネル以外では会話しない

    user_id = message.author.id
    update_user_state(user_id, message.content)

    response = generate_response_from_history(user_id)

    # 「にゃん」語尾を追加
    if user_styles.get(user_id) == "nyan":
        response += " " + random.choice(nyan_endings)

    await message.channel.send(response)
    await bot.process_commands(message)  # 他のコマンドも処理

# スラッシュコマンドの同期 & 起動メッセージ
@bot.event
async def on_ready():
    print(f"✅ ログインしました: {bot.user}")
    await bot.change_presence(activity=discord.Game(name="お話し中..."))

# ボット起動
bot.run(os.getenv("DISCORD_TOKEN"))
