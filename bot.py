import discord
from discord import app_commands
from discord.ext import commands
import random
import os
from dotenv import load_dotenv
from collections import defaultdict
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# .envファイルから設定を読み込む
load_dotenv()

# Botのインスタンス
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or("/"), intents=intents)
tree = bot.tree  # スラッシュコマンド用

# ユーザーごとの会話履歴管理 & 状態管理
user_states = defaultdict(lambda: {"conversation": []})
user_styles = {}
chat_channels = {}

# 軽量モデルのロード
device = torch.device("cpu")  # CPUで動作させる
model_name = "TinyLlama/TinyLlama-1.1B-intermediate-step"
model = None
tokenizer = None

def chat_with_bot(user_input):
    inputs = tokenizer(user_input, return_tensors="pt").to(device)
    outputs = model.generate(
        **inputs, max_length=30, num_return_sequences=1, no_repeat_ngram_size=2, top_p=0.9, temperature=0.7
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response[len(user_input):].strip()

@bot.event
async def on_ready():
    global model, tokenizer
    print(f"✅ ログインしました: {bot.user}")
    await bot.change_presence(activity=discord.Game(name="お話し中..."))
    model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    print("✅ モデルをロードしました！")

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

# ボット起動
bot.run(os.getenv("DISCORD_TOKEN"))
