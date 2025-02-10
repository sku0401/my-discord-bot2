import discord
from discord.ext import commands
import os
import random
import torch
import datetime
import time
import sys
import asyncio
from transformers import AutoModelForCausalLM, AutoTokenizer

# 環境変数からトークンを取得
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("DISCORD_TOKEN が設定されていません。環境変数を確認してください。")

# Discordボット設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 軽量なモデルのロード
print("軽量モデルをロードしています...")
try:
    tokenizer = AutoTokenizer.from_pretrained("rinna/japanese-gpt2-small", use_fast=False)
    model = AutoModelForCausalLM.from_pretrained("rinna/japanese-gpt2-small")

    # メモリ削減設定
    model.half()  # 半精度化 (float16)
    model.to("cpu")  # CPUへ移動
    model.eval()  # 推論モード
    print("モデルのロードが完了しました！")

except Exception as e:
    print(f"モデルのロード中にエラー: {e}")
    model = None  # モデルが読み込めなかった場合の対策

# ⏳ 指定時間外ならボットを停止する関数
def is_within_active_hours():
    """現在の時刻が 6:00 ～ 22:00 の範囲内か確認"""
    now = datetime.datetime.now().hour
    return 6 <= now < 22

async def shutdown_if_outside_hours():
    """指定時間外になったらボットを停止"""
    while True:
        if not is_within_active_hours():
            print("指定時間外になったためボットを終了します。")
            await bot.close()
            sys.exit()  # プロセスを終了
        await asyncio.sleep(60 * 10)  # 10分ごとにチェック

@bot.event
async def on_ready():
    """ボット起動時に呼ばれる"""
    await bot.tree.sync()  # スラッシュコマンドを同期
    print(f"Logged in as {bot.user.name}")
    bot.loop.create_task(shutdown_if_outside_hours())  # ⬅️ **ここで時間監視を開始**

# 各種コマンド
@bot.tree.command(name="talk", description="会話をする")
async def talk(interaction: discord.Interaction, user_input: str):
    if model is None:
        await interaction.response.send_message("現在、会話機能は利用できません（モデルのロードに失敗しました）。")
        return

    try:
        inputs = tokenizer(user_input, return_tensors="pt")

        with torch.no_grad():  # メモリ最適化
            outputs = model.generate(
                inputs['input_ids'],
                max_length=30,  # 出力を短縮してメモリ削減
                num_return_sequences=1,
                do_sample=True,
                top_p=0.9,
                temperature=0.8
            )
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)[:2000]

    except torch.cuda.OutOfMemoryError:
        response = "メモリ不足のため応答できません。"

    except Exception as e:
        response = f"エラーが発生しました: {str(e)}"

    await interaction.response.send_message(response)

@bot.tree.command(name="gacha", description="ガチャを引く")
async def gacha(interaction: discord.Interaction):
    items = ["決意", "忍耐", "勇気", "誠実", "不屈", "親切", "正義"]
    result = random.choice(items)
    await interaction.response.send_message(f"あなたが引いたのは: {result}！")

@bot.tree.command(name="nyan", description="猫のように応答する")
async def nyan(interaction: discord.Interaction):
    responses = ["にゃ～ん！", "にゃんにゃん♪", "ゴロゴロ…にゃん！"]
    response = random.choice(responses)
    await interaction.response.send_message(response)

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

# ボットを実行
def run_bot():
    bot.run(TOKEN)

if __name__ == "__main__":
    if is_within_active_hours():
        run_bot()
    else:
        print("現在、指定時間外のため起動しません。")
