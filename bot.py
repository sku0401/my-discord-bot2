import discord
from discord import app_commands
from discord.ext import commands
import random
import os
import logging
import json
from dotenv import load_dotenv
from flask import Flask
import threading
from collections import deque, defaultdict

# .envの読み込み
load_dotenv()

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flaskサーバー (UptimeRobot用)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)

threading.Thread(target=run_flask, daemon=True).start()

# Discord Bot の設定
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(intents=intents)

# データ管理
user_states = defaultdict(lambda: {"conversation": deque(maxlen=10)})
user_styles = {}
chat_channels = {}

# マルコフ連鎖による簡単な会話AI
class SimpleMarkovAI:
    def __init__(self):
        self.memory = defaultdict(list)

    def learn(self, text):
        words = text.split()
        for i in range(len(words) - 1):
            self.memory[words[i]].append(words[i + 1])

    def generate(self, text):
        words = text.split()
        if not words:
            return random.choice(list(self.memory.keys())) if self.memory else "..."
        current_word = words[-1]
        if current_word in self.memory:
            return current_word + " " + random.choice(self.memory[current_word])
        return random.choice(list(self.memory.keys())) if self.memory else "..."

markov_ai = SimpleMarkovAI()

# 会話履歴の更新
def update_user_state(user_id, message):
    user_states[user_id]["conversation"].append(message)
    markov_ai.learn(message)

# メッセージ処理
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    guild_id = message.guild.id if message.guild else None
    if guild_id and guild_id in chat_channels and message.channel.id != chat_channels[guild_id]:
        return
    
    user_id = message.author.id
    update_user_state(user_id, message.content)
    response = markov_ai.generate(message.content)
    
    if user_styles.get(user_id) == "nyan":
        response += " " + random.choice(["にゃん", "だにゃ", "なのにゃ", "にゃー！", "だよにゃ！"])
    
    await message.channel.send(response[:2000])

# スラッシュコマンド
@bot.tree.command(name="nyan", description="語尾がにゃん風になる")
async def nyan(interaction: discord.Interaction):
    user_styles[interaction.user.id] = "nyan"
    await interaction.response.send_message(f"{interaction.user.name}の語尾がにゃん風になったにゃん！")

@bot.tree.command(name="reset", description="口調を元に戻す")
async def reset(interaction: discord.Interaction):
    user_styles.pop(interaction.user.id, None)
    await interaction.response.send_message(f"{interaction.user.name}の口調が元に戻ったよ！")

@bot.tree.command(name="dice", description="n個のm面のダイスを振る (例: 2d6)")
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

# ボット起動
try:
    bot.run(os.getenv("DISCORD_TOKEN"))
except Exception as e:
    logger.error(f"❌ ボットの起動に失敗: {e}")
