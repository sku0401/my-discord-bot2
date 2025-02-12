import discord
from discord.ext import commands
import random
import os
import json
from dotenv import load_dotenv
from collections import defaultdict

# .envファイルの読み込み
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_TOKENが設定されていません。")

# ボットの設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ユーザーごとの会話履歴管理
user_states = defaultdict(lambda: {"conversation": []})

# 口調管理
user_styles = {}

# ランダムな会話リスト
talk_responses = [
    "こんにちは！今日はどうだった？",
    "元気だった？最近何か面白いことあった？",
    "お疲れ様～！今日はどんな感じだったかな？",
    "やっほ！最近どうしてたの～？",
    "こんにちはっ！今日も元気にいこうね！"
]

# 会話履歴から次の言葉をマルコフ連鎖風に生成
def generate_response_from_history(user_id):
    conversation = user_states[user_id]["conversation"]
    if len(conversation) < 2:
        return random.choice(talk_responses)

    last_message = conversation[-1].lower()
    if "元気" in last_message:
        return "えへへ、元気だよ～！"
    elif "疲れ" in last_message:
        return "ありがとう！今日はちょっと疲れたけど頑張るよ～！"
    else:
        return random.choice(talk_responses)

# ユーザーの会話履歴更新
def update_user_state(user_id, message):
    user_states[user_id]["conversation"].append(message)

# `/mesugaki` コマンド（メスガキ口調にする）
@bot.tree.command(name="mesugaki", description="メスガキ口調になる")
async def mesugaki(interaction: discord.Interaction):
    user_styles[interaction.user.id] = "mesugaki"
    await interaction.response.send_message(f"{interaction.user.name}はメスガキ口調になったにゃん！")

# `/nyan` コマンド（猫口調になる）
@bot.tree.command(name="nyan", description="猫っぽい口調になる")
async def nyan(interaction: discord.Interaction):
    user_styles[interaction.user.id] = "nyan"
    await interaction.response.send_message(f"{interaction.user.name}は猫口調になったにゃん！")

# `/reset` コマンド（口調を元に戻す）
@bot.tree.command(name="reset", description="口調を元に戻す")
async def reset(interaction: discord.Interaction):
    user_styles.pop(interaction.user.id, None)
    await interaction.response.send_message(f"{interaction.user.name}の口調が元に戻ったよ～！")

# メッセージを処理（ランダムな会話）
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id
    update_user_state(user_id, message.content)

    response = generate_response_from_history(user_id)

    # 口調の変更
    if user_id in user_styles:
        if user_styles[user_id] == "mesugaki":
            response = "うるさいにゃん！こっち来いよ、早くにゃ！"
        elif user_styles[user_id] == "nyan":
            response += " にゃん！"

    await message.channel.send(response)
    await bot.process_commands(message)

# `/dice` コマンド（ダイスロール）
@bot.tree.command(name="dice", description="ダイスを振る (例: /dice 2d6)")
async def dice(interaction: discord.Interaction, dice_input: str):
    try:
        num_dice, dice_sides = map(int, dice_input.lower().split('d'))
        rolls = [random.randint(1, dice_sides) for _ in range(num_dice)]
        total = sum(rolls)
        roll_result = ', '.join(map(str, rolls))
        await interaction.response.send_message(f"ロール結果は：{roll_result} (合計: {total}) だよ～！")
    except ValueError:
        await interaction.response.send_message("入力形式が違うみたい。「2d6」みたいに入力してね！")

# `/janken` コマンド（じゃんけん）
class JankenView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(JankenButton(label="グー", custom_id="rock"))
        self.add_item(JankenButton(label="チョキ", custom_id="scissors"))
        self.add_item(JankenButton(label="パー", custom_id="paper"))

class JankenButton(discord.ui.Button):
    async def callback(self, interaction: discord.Interaction):
        hands = {"rock": "グー", "scissors": "チョキ", "paper": "パー"}
        user_hand = hands[self.custom_id]
        bot_hand = random.choice(list(hands.values()))

        results = {
            ("グー", "チョキ"): "あなたの勝ち～！",
            ("チョキ", "パー"): "あなたの勝ち～！",
            ("パー", "グー"): "あなたの勝ち～！",
            ("チョキ", "グー"): "あなたの負け～。",
            ("パー", "チョキ"): "あなたの負け～。",
            ("グー", "パー"): "あなたの負け～。",
        }
        result = results.get((user_hand, bot_hand), "あいこだね～！")

        await interaction.response.send_message(f"あなた: {user_hand} - ボット: {bot_hand}\n結果: {result}")

@bot.tree.command(name="janken", description="じゃんけんをする")
async def janken(interaction: discord.Interaction):
    await interaction.response.send_message("じゃんけんをしよう！", view=JankenView())

# `/help` コマンド（ヘルプ）
@bot.tree.command(name="help", description="コマンド一覧を表示")
async def help(interaction: discord.Interaction):
    help_text = """
    **コマンド一覧:**
    - `/dice 2d6`: ダイスを振る
    - `/janken`: じゃんけんをする
    - `/mesugaki`: メスガキ口調になる
    - `/nyan`: 猫口調になる
    - `/reset`: 口調を元に戻す
    - `/help`: コマンド一覧を表示
    """
    await interaction.response.send_message(help_text)

# ボットの起動
bot.run(TOKEN)
