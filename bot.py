import discord
from discord import app_commands
from discord.ext import commands
import random
import os
from dotenv import load_dotenv
from flask import Flask
import threading
from collections import defaultdict
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch

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
bot = commands.Bot(command_prefix=commands.when_mentioned_or("/"), intents=intents)
tree = bot.tree  # スラッシュコマンド用

# ユーザーごとの会話履歴管理 & 状態管理
user_states = defaultdict(lambda: {"conversation": []})
user_styles = {}

# 設定した会話チャンネル
chat_channels = {}

# Hugging Faceのモデルをローカルで使用
model_name = "distilgpt2"
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

def chat_with_bot(user_input):
    inputs = tokenizer(user_input, return_tensors="pt")
    with torch.no_grad():  # メモリ節約のため勾配計算を無効化
        outputs = model.generate(**inputs, max_length=50, num_return_sequences=1, no_repeat_ngram_size=2, top_p=0.95, temperature=0.7)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response[len(user_input):].strip()

# メッセージイベント: 会話システム
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    guild_id = message.guild.id if message.guild else None
    if guild_id and guild_id in chat_channels and message.channel.id != chat_channels[guild_id]:
        return

    user_id = message.author.id
    user_states[user_id]["conversation"].append(message.content)

    response = chat_with_bot(message.content)
    if user_styles.get(user_id) == "nyan":
        response += " " + random.choice(["にゃん", "だにゃ", "なのにゃ", "にゃー！", "だよにゃ！"])
    
    await message.channel.send(response)

# スラッシュコマンドの登録
@tree.command(name="nyan", description="語尾がにゃん風になる")
async def nyan(interaction: discord.Interaction):
    user_styles[interaction.user.id] = "nyan"
    await interaction.response.send_message(f"{interaction.user.name}の語尾がにゃん風になったにゃん！")

@tree.command(name="reset", description="口調を元に戻す")
async def reset(interaction: discord.Interaction):
    user_styles.pop(interaction.user.id, None)
    await interaction.response.send_message(f"{interaction.user.name}の口調が元に戻ったよ！")

@tree.command(name="setchannel", description="このチャンネルを会話チャンネルに設定する")
async def setchannel(interaction: discord.Interaction):
    chat_channels[interaction.guild.id] = interaction.channel.id
    await interaction.response.send_message("このチャンネルを会話チャンネルに設定したよ！")

@tree.command(name="unsetchannel", description="会話チャンネルの設定を解除する")
async def unsetchannel(interaction: discord.Interaction):
    if interaction.guild.id in chat_channels:
        del chat_channels[interaction.guild.id]
        await interaction.response.send_message("会話チャンネルの設定を解除したよ！")
    else:
        await interaction.response.send_message("会話チャンネルはまだ設定されていないよ！")

@tree.command(name="dice", description="n個のm面のダイスを振る (例: 2d6)")
async def dice(interaction: discord.Interaction, dice_input: str):
    try:
        num_dice, dice_sides = map(int, dice_input.lower().split('d'))
        if num_dice < 1 or dice_sides < 1:
            raise ValueError("正の整数を指定してください！")
        
        rolls = [random.randint(1, dice_sides) for _ in range(num_dice)]
        total = sum(rolls)
        roll_result = ', '.join(map(str, rolls))
        await interaction.response.send_message(f"🎲 ロール結果: {roll_result} (合計: {total})")
    
    except ValueError:
        await interaction.response.send_message("⚠️ 入力形式が間違ってるよ！「2d6」みたいに入力してね！")

# スラッシュコマンドの同期 & 起動メッセージ
@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ ログインしました: {bot.user}")
    await bot.change_presence(activity=discord.Game(name="お話し中..."))

# ボット起動
bot.run(os.getenv("DISCORD_TOKEN"))
