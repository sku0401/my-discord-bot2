import discord
from discord.ext import commands
import os
from transformers import AutoModelForCausalLM, AutoTokenizer
import random

# Discordボット設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# モデルと会話ログの初期化
tokenizer = None
model = None
conversation_log = []

# モデルのロードとボット起動確認
@bot.event
async def on_ready():
    global tokenizer, model
    if tokenizer is None or model is None:
        print("モデルをロードしています...")
        tokenizer = AutoTokenizer.from_pretrained("rinna/japanese-gpt-1b", use_fast=False)
        model = AutoModelForCausalLM.from_pretrained("rinna/japanese-gpt-1b")
    await bot.tree.sync()
    print(f"Logged in as {bot.user.name}")

# 会話コマンド
@bot.tree.command(name="talk", description="会話をする")
async def talk(interaction: discord.Interaction, user_input: str):
    conversation_log.append(f"User: {user_input}")
    inputs = tokenizer(user_input, return_tensors="pt")
    outputs = model.generate(
        inputs['input_ids'],
        max_length=100,
        num_return_sequences=1,
        do_sample=True,
        top_p=0.9,
        temperature=0.8
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)[:2000]
    conversation_log.append(f"Bot: {response}")
    await interaction.response.send_message(response)

# ガチャコマンド
@bot.tree.command(name="gacha", description="ガチャを引く")
async def gacha(interaction: discord.Interaction):
    items = ["決意", "忍耐", "勇気", "誠実", "不屈", "親切", "正義"]
    result = random.choice(items)
    await interaction.response.send_message(f"あなたが引いたのは: {result}！")

# にゃんコマンド
@bot.tree.command(name="nyan", description="猫のように応答する")
async def nyan(interaction: discord.Interaction):
    responses = ["にゃ～ん！", "にゃんにゃん♪", "ゴロゴロ…にゃん！"]
    response = random.choice(responses)
    await interaction.response.send_message(response)

# ダイスロールコマンド
@bot.tree.command(name="dice", description="指定したダイスのロールを行う（例：2d6）")
async def dice(interaction: discord.Interaction, dice_input: str):
    try:
        num_dice, dice_sides = map(int, dice_input.split('d'))
        rolls = [random.randint(1, dice_sides) for _ in range(num_dice)]
        total = sum(rolls)
        roll_result = ', '.join(map(str, rolls))
        await interaction.response.send_message(f"ロール結果: {roll_result} (合計: {total})")
    except ValueError:
        await interaction.response.send_message("入力形式が正しくありません。正しい形式は「○d○」です。例: 2d6")

# じゃんけんコマンド
@bot.tree.command(name="janken", description="じゃんけんをする (グー, チョキ, パー)")
async def janken(interaction: discord.Interaction, user_hand: str):
    if user_hand not in ["グー", "チョキ", "パー"]:
        await interaction.response.send_message("正しい手を入力してください: グー, チョキ, パー")
        return
    hands = ["グー", "チョキ", "パー"]
    bot_hand = random.choice(hands)
    if user_hand == bot_hand:
        result = "あいこ！"
    elif (user_hand == "グー" and bot_hand == "チョキ") or \
         (user_hand == "チョキ" and bot_hand == "パー") or \
         (user_hand == "パー" and bot_hand == "グー"):
        result = "あなたの勝ち！"
    else:
        result = "あなたの負け！"
    await interaction.response.send_message(f"ボットの手: {bot_hand} - {result}")

# 会話ログ保存コマンド
@bot.tree.command(name="save_log", description="会話ログを保存する")
async def save_log(interaction: discord.Interaction):
    log_path = "conversation_log.txt"
    try:
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("\n".join(conversation_log))
        await interaction.response.send_message(f"会話ログを{log_path}に保存しました！")
    except Exception as e:
        await interaction.response.send_message(f"ログ保存中にエラーが発生しました: {e}")

# エラーハンドリング
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandInvokeError):
        await ctx.send("コマンドの実行中にエラーが発生しました。再試行してください。")
    else:
        await ctx.send(f"エラー: {error}")

# ボットの起動処理
def run_bot():
    try:
        token = os.getenv('MY_TOKEN')  # 環境変数 'MY_TOKEN' から取得
        if not token:
            raise ValueError("トークンが設定されていません。環境変数 'MY_TOKEN' を確認してください。")
        bot.run(token)
    except Exception as e:
        print(f"エラー発生: {e}")

if __name__ == "__main__":
    run_bot()
import discord
from discord.ext import commands
import os
from transformers import AutoModelForCausalLM, AutoTokenizer
import random

# Discordボット設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# モデルと会話ログの初期化
tokenizer = None
model = None
conversation_log = []

# モデルのロードとボット起動確認
@bot.event
async def on_ready():
    global tokenizer, model
    if tokenizer is None or model is None:
        print("モデルをロードしています...")
        tokenizer = AutoTokenizer.from_pretrained("rinna/japanese-gpt-1b", use_fast=False)
        model = AutoModelForCausalLM.from_pretrained("rinna/japanese-gpt-1b")
    await bot.tree.sync()
    print(f"Logged in as {bot.user.name}")

# 会話コマンド
@bot.tree.command(name="talk", description="会話をする")
async def talk(interaction: discord.Interaction, user_input: str):
    conversation_log.append(f"User: {user_input}")
    inputs = tokenizer(user_input, return_tensors="pt")
    outputs = model.generate(
        inputs['input_ids'],
        max_length=100,
        num_return_sequences=1,
        do_sample=True,
        top_p=0.9,
        temperature=0.8
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)[:2000]
    conversation_log.append(f"Bot: {response}")
    await interaction.response.send_message(response)

# ガチャコマンド
@bot.tree.command(name="gacha", description="ガチャを引く")
async def gacha(interaction: discord.Interaction):
    items = ["決意", "忍耐", "勇気", "誠実", "不屈", "親切", "正義"]
    result = random.choice(items)
    await interaction.response.send_message(f"あなたが引いたのは: {result}！")

# にゃんコマンド
@bot.tree.command(name="nyan", description="猫のように応答する")
async def nyan(interaction: discord.Interaction):
    responses = ["にゃ～ん！", "にゃんにゃん♪", "ゴロゴロ…にゃん！"]
    response = random.choice(responses)
    await interaction.response.send_message(response)

# ダイスロールコマンド
@bot.tree.command(name="dice", description="指定したダイスのロールを行う（例：2d6）")
async def dice(interaction: discord.Interaction, dice_input: str):
    try:
        num_dice, dice_sides = map(int, dice_input.split('d'))
        rolls = [random.randint(1, dice_sides) for _ in range(num_dice)]
        total = sum(rolls)
        roll_result = ', '.join(map(str, rolls))
        await interaction.response.send_message(f"ロール結果: {roll_result} (合計: {total})")
    except ValueError:
        await interaction.response.send_message("入力形式が正しくありません。正しい形式は「○d○」です。例: 2d6")

# じゃんけんコマンド
@bot.tree.command(name="janken", description="じゃんけんをする (グー, チョキ, パー)")
async def janken(interaction: discord.Interaction, user_hand: str):
    if user_hand not in ["グー", "チョキ", "パー"]:
        await interaction.response.send_message("正しい手を入力してください: グー, チョキ, パー")
        return
    hands = ["グー", "チョキ", "パー"]
    bot_hand = random.choice(hands)
    if user_hand == bot_hand:
        result = "あいこ！"
    elif (user_hand == "グー" and bot_hand == "チョキ") or \
         (user_hand == "チョキ" and bot_hand == "パー") or \
         (user_hand == "パー" and bot_hand == "グー"):
        result = "あなたの勝ち！"
    else:
        result = "あなたの負け！"
    await interaction.response.send_message(f"ボットの手: {bot_hand} - {result}")

# 会話ログ保存コマンド
@bot.tree.command(name="save_log", description="会話ログを保存する")
async def save_log(interaction: discord.Interaction):
    log_path = "conversation_log.txt"
    try:
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("\n".join(conversation_log))
        await interaction.response.send_message(f"会話ログを{log_path}に保存しました！")
    except Exception as e:
        await interaction.response.send_message(f"ログ保存中にエラーが発生しました: {e}")

# エラーハンドリング
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandInvokeError):
        await ctx.send("コマンドの実行中にエラーが発生しました。再試行してください。")
    else:
        await ctx.send(f"エラー: {error}")

# ボットの起動処理
def run_bot():
    try:
        token = os.getenv('MY_TOKEN')  # 環境変数 'MY_TOKEN' から取得
        if not token:
            raise ValueError("トークンが設定されていません。環境変数 'MY_TOKEN' を確認してください。")
        bot.run(token)
    except Exception as e:
        print(f"エラー発生: {e}")

if __name__ == "__main__":
    run_bot()

