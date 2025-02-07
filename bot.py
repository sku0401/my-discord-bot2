import discord
from discord.ext import commands
import os
import random
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# 環境変数からトークンを取得
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("DISCORD_TOKEN が設定されていません。環境変数を確認してください。")

# Discordボット設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 軽量化した日本語モデルを指定
MODEL_NAME = "rinna/japanese-gpt-neo-125M"

# モデルを遅延ロード（Lazy Load）
tokenizer = None
model = None

# メモリ節約のためにロードを遅延
def load_model():
    global tokenizer, model
    if tokenizer is None or model is None:
        print("モデルをロードしています...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=False)
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME, 
            device_map="auto",  # 自動で最適なデバイスに配置
            torch_dtype=torch.float16  # メモリ節約のためにfloat16を使用
        )
        print("モデルのロードが完了しました！")

@bot.event
async def on_ready():
    await bot.tree.sync()  # スラッシュコマンドを同期
    print(f"Logged in as {bot.user.name}")

# 会話コマンド
@bot.tree.command(name="talk", description="会話をする")
async def talk(interaction: discord.Interaction, user_input: str):
    try:
        load_model()  # コマンド実行時に初めてモデルをロード
        inputs = tokenizer(user_input, return_tensors="pt").to("cpu")  # CPUで実行
        outputs = model.generate(
            inputs['input_ids'],
            max_length=50,  # max_lengthを短くしてメモリ削減
            num_return_sequences=1,
            do_sample=True,
            top_p=0.9,
            temperature=0.8
        )
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)[:2000]
    except Exception as e:
        response = f"エラーが発生しました: {str(e)}"
    
    # ログをファイルに保存
    with open("conversation_log.txt", "a", encoding="utf-8") as f:
        f.write(f"User: {user_input}\nBot: {response}\n")

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

    results = {
        ("グー", "チョキ"): "あなたの勝ち！",
        ("チョキ", "パー"): "あなたの勝ち！",
        ("パー", "グー"): "あなたの勝ち！",
        ("チョキ", "グー"): "あなたの負け！",
        ("パー", "チョキ"): "あなたの負け！",
        ("グー", "パー"): "あなたの負け！"
    }

    result = results.get((user_hand, bot_hand), "あいこ！")
    await interaction.response.send_message(f"ボットの手: {bot_hand} - {result}")

def run_bot():
    bot.run(TOKEN)

if __name__ == "__main__": 
    run_bot()
