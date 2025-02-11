import discord
from discord.ext import commands
import random
import asyncio
import os
from dotenv import load_dotenv
from flask import Flask

# .envファイルを読み込む
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Discordボット設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 会話の状態を管理
talking_users = {}

# 初期の口調
tone = "normal"

# ランダムな会話リスト
talk_responses = [
    "こんにちはっ！元気だった？",
    "やっほ～！今日はどんな一日だったかな？",
    "お疲れさま～！今日はどうだった？",
    "こんちゃ～！最近何か楽しいことあった？",
    "やっほ！何かお話ししたいことあったら教えてね♪",
    "おっす！元気そうだね！",
    "こんにちは～！今日は何をしてるのかな？",
    "あ～、なんかドキドキしちゃう！何か話してくれるかな？",
    "おつかれさま～！どうしたの？",
    "こんにちはっ！お話ししようよ～！",
    "やっほ～！最近どう？",
    "おっ！元気そうだね、嬉しいな！",
    "えへへ、こんにちは！今日も元気にいこうね！",
    "やったー！会えて嬉しいよ～！",
    "こんにちはーっ！なんか面白いことないかな？",
    "わーい、久しぶりに会えたね！どうだった最近？",
    "こんにちはっ！今日は何をしてるの～？",
    "やっほ～！最近何か面白いことあった？",
    "おー、こんにちは～！元気？",
    "こんちゃ～！何かお話ししようよ～♪",
    "こんにちはっ！最近どうかな？",
    "やっほ～！元気そうでよかった♪",
    "お疲れさま～！今日はどうだった～？",
    "あ～、なんだかドキドキするよ～！",
    "こんにちは～！今日もよろしくね！",
    "やった！会えて嬉しいよ！",
    "おっす！今日も楽しくお話ししようね！",
    "やっほ～！どうしたんだい？",
    "こんにちは！今日は何か面白いことあったかな？",
    "お疲れ様～！どうしたの～？",
    "こんにちは！今日は何してるの～？",
    "おー！こんにちは～！何か話そうよ～",
    "やっほ！今日はどんなことしてるの～？",
    "こんにちはっ！あっ、もしかしてお話したいことがあるの？",
    "えへへ、元気だよ！何か話してくれるかな？",
    "こんにちは～！最近どうしてたのかな？",
    "やっほ～！今日も楽しく過ごしてる？",
    "おつかれさま～！最近何してたの～？",
    "こんにちは！今日はどんなことしてるのかな～？",
    "やっほ！最近どうだった～？",
    "こんにちはっ！今日は楽しいことあった～？",
    "やっほ～！元気そうでよかった～！",
    "お疲れ様～！今日はどんな一日だったかな？",
    "こんにちはっ！今日は何してるのかな～？",
    "やっほ～！お話ししたいことがあったら言ってね！"
]

# 口調ごとの変化
def get_tone_response(response):
    global tone
    if tone == "casual":
        return response + " えへへ、どうしたの～？"
    elif tone == "formal":
        return "お疲れ様です。何かお話があればお聞きします。"
    return response + " なんだか嬉しいな～"

# ボット準備完了時の処理
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"ログインしました: {bot.user}")

# ボットがメンションされた時の会話
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if bot.user in message.mentions:
        user_id = message.author.id
        talking_users[user_id] = asyncio.time()

        response = get_tone_response(random.choice(talk_responses))
        await message.channel.send(response)

        async def end_conversation():
            await asyncio.sleep(30)
            if user_id in talking_users:
                last_time = talking_users[user_id]
                if asyncio.time() - last_time >= 30:
                    del talking_users[user_id]
                    await message.channel.send("えへへ、そろそろお話終わりかな～？また話しかけてね♪")

        asyncio.create_task(end_conversation())

    elif message.author.id in talking_users:
        talking_users[message.author.id] = asyncio.time()
        response = get_tone_response(random.choice(talk_responses))
        await message.channel.send(response)

    await bot.process_commands(message)

# /talk コマンド
@bot.tree.command(name="talk", description="ランダムでおっとり系の会話をする")
async def talk(interaction: discord.Interaction):
    response = get_tone_response(random.choice(talk_responses))
    await interaction.response.send_message(response)

# /gacha コマンド
@bot.tree.command(name="gacha", description="ガチャを引いて結果を表示")
async def gacha(interaction: discord.Interaction):
    items = ["決意", "忍耐", "勇気", "誠実", "不屈", "親切", "正義"]
    result = random.choice(items)
    await interaction.response.send_message(f"わぁ～！あなたが引いたのは「{result}」だよ～！一緒に頑張ろうね！")

# /nyan コマンド
@bot.tree.command(name="nyan", description="猫のように応答する")
async def nyan(interaction: discord.Interaction):
    responses = ["にゃ～ん！", "にゃんにゃん♪", "ゴロゴロ…にゃん！", "にゃ～ん、いっしょに遊ぼうよ！"]
    response = random.choice(responses)
    await interaction.response.send_message(response)

# /dice コマンド
@bot.tree.command(name="dice", description="指定したダイスをロールして結果を表示")
async def dice(interaction: discord.Interaction, dice_input: str):
    try:
        num_dice, dice_sides = map(int, dice_input.split('d'))
        rolls = [random.randint(1, dice_sides) for _ in range(num_dice)]
        total = sum(rolls)
        roll_result = ', '.join(map(str, rolls))
        await interaction.response.send_message(f"ロール結果は：{roll_result} (合計: {total}) だよ～！ワクワクしちゃうね！")
    except ValueError:
        await interaction.response.send_message("うーん、入力形式が違うみたい。「2d6」みたいに入力してね！")

# /janken コマンド
@bot.tree.command(name="janken", description="じゃんけんをする (グー, チョキ, パー)")
async def janken(interaction: discord.Interaction, user_hand: str):
    if user_hand not in ["グー", "チョキ", "パー"]:
        await interaction.response.send_message("「グー」「チョキ」「パー」から選んでね！")
        return

    hands = ["グー", "チョキ", "パー"]
    bot_hand = random.choice(hands)

    results = {
        ("グー", "チョキ"): "あなたの勝ち～！やったね！",
        ("チョキ", "パー"): "あなたの勝ち～！すごいね！",
        ("パー", "グー"): "あなたの勝ち～！おめでとう！",
        ("チョキ", "グー"): "あなたの負けだよ～。また挑戦してね！",
        ("パー", "チョキ"): "あなたの負けだよ～。次頑張ろうね！",
        ("グー", "パー"): "あなたの負けだよ～。次はきっと勝てるよ！"
    }

    result = results.get((user_hand, bot_hand), "あいこだね～！もう一回しようよ！")
    await interaction.response.send_message(f"あなた: {user_hand} - ボット: {bot_hand}\n結果: {result}")

# /compliment コマンド
@bot.tree.command(name="compliment", description="褒めるメッセージをランダムで表示")
async def compliment(interaction: discord.Interaction):
    responses = [
        "すごいね～！あなたって本当に素敵だな♪",
        "うわぁ、あなたってなんて素晴らしいんだろう！",
        "あっ、あなたの笑顔最高！癒される～",
        "よく頑張ったね！すごいよ～！"
    ]
    response = random.choice(responses)
    await interaction.response.send_message(response)

# /hug コマンド
@bot.tree.command(name="hug", description="ハグをランダムで送る")
async def hug(interaction: discord.Interaction):
    responses = ["ギュッとしちゃうよ～！", "ふふっ、ハグしちゃうね～！", "ギューってしてあげる！"]
    response = random.choice(responses)
    await interaction.response.send_message(response)

# /sleep コマンド
@bot.tree.command(name="sleep", description="おやすみメッセージを送る")
async def sleep(interaction: discord.Interaction):
    responses = ["おやすみ～！いい夢を見てね！", "ぐっすり眠ってね～！", "おやすみなさい！ゆっくり休んでね～"]
    response = random.choice(responses)
    await interaction.response.send_message(response)

# Flask部分
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))  # 環境変数 PORT があればそれを使う
    app.run(host="0.0.0.0", port=port)

# Discord Bot を実行
bot.run(TOKEN)
