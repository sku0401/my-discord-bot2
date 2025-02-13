import discord
from discord import app_commands
import random
import os
from dotenv import load_dotenv

# .envファイルから設定を読み込む
load_dotenv()

# ボットのインスタンスとインテント設定
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# ユーザーごとの会話履歴管理 & 状態管理
user_states = {}
user_styles = {}

# 設定した会話チャンネル
chat_channels = {}

# 会話パターン
talk_responses = [
    "こんにちは！今日はどんな日だった？",
    "元気だった？最近何か面白いことあった？",
    "お疲れ様～！無理しすぎてない？",
    "やっほ！最近どうしてたの？",
    "こんにちは！今日も元気にいこうね！",
    "おなか空いた…ごはんはもう食べた？",
    "今日は何して遊ぶの？",
    "ふわぁ…ちょっと眠いかも。",
    "今日の天気はどうだった？外に出た？",
    "ねぇねぇ、好きな食べ物は何？",
    "むむ、ちょっと退屈かも。何か面白いことしてる？",
    "宿題終わった？それともまだやってない？",
    "最近の流行りって何か知ってる？",
    "新しいゲームとかアニメとか見た？",
    "どこか旅行行きたい場所ある？",
    "最近ハマってることある？",
    "好きな色は何？私は白と青が好き！",
    "今日もいい日だった？それとも微妙？",
    "困ったことがあったら話してもいいんだよ？",
    "お昼寝って最高だよね～",
    "ちょっとストレッチしたら気持ちいいよ！",
    "最近頑張ったことある？聞かせて！",
    "もふもふしたい気分。",
    "何か面白い話ある？",
    "今日はどんな音楽聴いた？",
    "ゲームするなら何が好き？",
    "お菓子食べたくなってきた！",
    "今度一緒に遊びたいな～！",
    "たまにはゆっくり休むのも大事！",
    "好きな動物って何？私は猫も犬も好き～！",
    "最近見た夢ってどんなのだった？",
    "夜更かししすぎてない？ちゃんと寝てる？",
    "運動不足になってない？たまには体動かすといいよ！",
    "あれ？今何しようとしてたっけ…忘れちゃった！",
    "新しい趣味とか始めたいことある？",
    "ちょっとリラックスしてお茶でも飲もう。",
    "甘いものとしょっぱいもの、どっちが好き？",
    "ぼーっとする時間も大事！",
    "友達と遊ぶのも楽しいよね！",
    "ちょっとだけサボっちゃおうかな？",
    "元気がない時は深呼吸するといいよ～",
    "ふわふわのクッションで寝たいな～",
    "笑顔になれることって大事だよね！",
    "ねぇねぇ、面白い話して！",
    "猫カフェ行ったことある？もふもふ最高！",
    "たまには何も考えずにぼーっとするのもいいよね～",
    "疲れたら甘いもの食べるといいよ！",
    "何かお手伝いできることある？",
    "そろそろ休憩しよっか？",
    "おしゃべり楽しいな！",
    "星を眺めるのってロマンチックだよね～",
    "寒い時はちゃんとあったかくするんだよ！",
    "暑い日は水分補給忘れずにね！",
    "ねむねむ…ちょっとだけ寝てもいい？",
    "大丈夫！きっとうまくいくよ！",
    "今日はどんな夢見たい？楽しい夢が見れるといいね～",
    "いっぱい遊んだあとはゆっくり休もう！",
    "お話してると時間があっという間に過ぎちゃうね！"
]

# 「にゃん」語尾リスト
nyan_endings = ["にゃん", "だにゃ", "なのにゃ", "にゃー！", "だよにゃ！"]

# 会話履歴から次の言葉を生成
def generate_response_from_history(user_id):
    conversation_history = user_states.get(user_id, {"conversation": []})["conversation"]
    
    if len(conversation_history) < 2:
        return random.choice(talk_responses)

    last_message = conversation_history[-1]
    if "疲れた" in last_message:
        return "お疲れ様～！無理しないでね！"
    elif "元気" in last_message:
        return "えへへ、元気いっぱいだよ～！"
    else:
        return random.choice(talk_responses)

# ユーザーの会話履歴更新
def update_user_state(user_id, message):
    if user_id not in user_states:
        user_states[user_id] = {"conversation": []}
    user_states[user_id]["conversation"].append(message)

# スラッシュコマンド: 語尾を「にゃん」系にする
@tree.command(name="nyan", description="語尾がにゃん風になる")
async def nyan(interaction: discord.Interaction):
    user_styles[interaction.user.id] = "nyan"
    await interaction.response.send_message(f"{interaction.user.name}の語尾がにゃん風になったにゃん！")

# スラッシュコマンド: 口調リセット
@tree.command(name="reset", description="口調を元に戻す")
async def reset(interaction: discord.Interaction):
    if interaction.user.id in user_styles:
        del user_styles[interaction.user.id]
    await interaction.response.send_message(f"{interaction.user.name}の口調が元に戻ったにゃ！")

# スラッシュコマンド: 会話チャンネル設定
@tree.command(name="setchannel", description="このチャンネルを会話チャンネルに設定する")
async def setchannel(interaction: discord.Interaction):
    chat_channels[interaction.guild.id] = interaction.channel.id
    await interaction.response.send_message("このチャンネルを会話チャンネルに設定したにゃ！")

# スラッシュコマンド: ダイスロール
@tree.command(name="dice", description="n個のm面のダイスを振る (例: 2d6)")
async def dice(interaction: discord.Interaction, dice_input: str):
    try:
        num_dice, dice_sides = map(int, dice_input.split('d'))
        rolls = [random.randint(1, dice_sides) for _ in range(num_dice)]
        total = sum(rolls)
        roll_result = ', '.join(map(str, rolls))
        await interaction.response.send_message(f"ロール結果は：{roll_result} (合計: {total}) だにゃ！")
    except ValueError:
        await interaction.response.send_message("うーん、入力形式が違うみたい。「2d6」みたいに入力してにゃ！")

# メンションでの会話
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    guild_id = message.guild.id if message.guild else None
    if guild_id and guild_id in chat_channels and message.channel.id != chat_channels[guild_id]:
        return  # 設定されたチャンネル以外では反応しない

    user_id = message.author.id
    update_user_state(user_id, message.content)

    response = generate_response_from_history(user_id)

    # 「にゃん」語尾を追加
    if user_id in user_styles and user_styles[user_id] == "nyan":
        response += " " + random.choice(nyan_endings)

    await message.channel.send(response)

# スラッシュコマンドの同期
@bot.event
async def on_ready():
    await tree.sync()
    print(f"ログインしました: {bot.user}")

# Render用のポート指定
PORT = int(os.getenv("PORT", 8080))

# ボット起動
bot.run(os.getenv("DISCORD_TOKEN"))
