import discord
from discord.ext import commands
import random

# Discordボット設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 口調設定用の変数
tone = "normal"

# ランダムなtalkコマンドの反応（女の子っぽい感じで）
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

# 褒めるメッセージ
compliment_responses = [
    "すごいね～！あなたって本当に素敵だな♪",
    "うわぁ、あなたってなんて素晴らしいんだろう！",
    "あっ、あなたの笑顔最高！癒される～",
    "よく頑張ったね！すごいよ～！",
    "すごい！あなたってほんとに優しいね♪",
    "わぁ、あなたがいると嬉しいな～！"
]

# ハグメッセージ
hug_responses = [
    "ギュッとしちゃうよ～！あったかいね♡",
    "ふふっ、ハグしちゃうね～！あったかくて安心する～",
    "ギューってしてあげる！なんだかホッとするね♪"
]

# おやすみメッセージ
sleep_responses = [
    "おやすみ～！いい夢を見てね！",
    "ぐっすり眠ってね～！おやすみなさい♪",
    "おやすみなさい！ゆっくり休んでね～"
]

# コマンドの実行
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

# /talk: ランダムでおっとり系の会話を返答
@bot.tree.command(name="talk", description="ランダムでおっとり系の会話をする")
async def talk(interaction: discord.Interaction):
    response = random.choice(talk_responses)
    
    if tone == "casual":
        response += " えへへ、どうしたの～？"
    elif tone == "formal":
        response = "お疲れ様です。何かお話があればお聞きします。"
    else:  # 通常の反応
        response += " なんだか嬉しいな～"
    
    await interaction.response.send_message(response)

# /gacha: ガチャを引いて結果を表示
@bot.tree.command(name="gacha", description="ガチャを引いて結果を表示")
async def gacha(interaction: discord.Interaction):
    items = ["決意", "忍耐", "勇気", "誠実", "不屈", "親切", "正義"]
    result = random.choice(items)
    await interaction.response.send_message(f"わぁ～！あなたが引いたのは「{result}」だよ～！一緒に頑張ろうね！")

# /nyan: 猫のように応答する
@bot.tree.command(name="nyan", description="猫のように応答する")
async def nyan(interaction: discord.Interaction):
    responses = ["にゃ～ん！", "にゃんにゃん♪", "ゴロゴロ…にゃん！", "にゃ～ん、いっしょに遊ぼうよ！"]
    response = random.choice(responses)
    await interaction.response.send_message(response)

# /dice: 指定したダイスをロールして結果を表示
@bot.tree.command(name="dice", description="指定したダイスをロールして結果を表示")
async def dice(interaction: discord.Interaction, dice_input: str):
    try:
        num_dice, dice_sides = map(int, dice_input.split('d'))
        rolls = [random.randint(1, dice_sides) for _ in range(num_dice)]
        total = sum(rolls)
        roll_result = ', '.join(map(str, rolls))
        await interaction.response.send_message(f"わぁ～！ロール結果は：{roll_result} (合計: {total}だよ～！ワクワクしちゃうね！)")
    except ValueError:
        await interaction.response.send_message("うーん、入力形式が間違ってるみたい。正しい形式は「○d○」だよ～！例えば「2d6」って入力してね！")

# /janken: じゃんけんをして結果を表示
@bot.tree.command(name="janken", description="じゃんけんをする (グー, チョキ, パー)")
async def janken(interaction: discord.Interaction, user_hand: str):
    if user_hand not in ["グー", "チョキ", "パー"]:
        await interaction.response.send_message("うーん、正しい手を入力してね～！「グー」「チョキ」「パー」だよ！")
        return
    
    hands = ["グー", "チョキ", "パー"]
    bot_hand = random.choice(hands)

    results = {
        ("グー", "チョキ"): "あなたの勝ち～！やったね！",
        ("チョキ", "パー"): "あなたの勝ち～！すごいね！",
        ("パー", "グー"): "あなたの勝ち～！おめでとう！",
        ("チョキ", "グー"): "あ～、あなたの負けだよ～。でも、また挑戦してね！",
        ("パー", "チョキ"): "あ～、あなたの負けだよ～。次頑張ろうね！",
        ("グー", "パー"): "あ～、あなたの負けだよ～。でも次はきっと勝てるよ！"
    }

    result = results.get((user_hand, bot_hand), "あいこだね～！もう一回しようよ！")
    await interaction.response.send_message(f"あなた: {user_hand} - ボット: {bot_hand}\n結果: {result}")

# /compliment: 褒めるメッセージをランダムで表示
@bot.tree.command(name="compliment", description="褒めるメッセージをランダムで表示")
async def compliment(interaction: discord.Interaction):
    response = random.choice(compliment_responses)
    await interaction.response.send_message(response)

# /hug: ハグをランダムで送る
@bot.tree.command(name="hug", description="ハグをランダムで送る")
async def hug(interaction: discord.Interaction):
    response = random.choice(hug_responses)
    await interaction.response.send_message(response)

# /sleep: おやすみメッセージを送る
@bot.tree.command(name="sleep", description="おやすみメッセージを送る")
async def sleep(interaction: discord.Interaction):
    response = random.choice(sleep_responses)
    await interaction.response.send_message(response)

# Discord Bot を実行
bot.run("YOUR_DISCORD_TOKEN")
