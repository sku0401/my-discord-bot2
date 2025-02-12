import discord
from discord.ext import commands
import random
import json
import os
from dotenv import load_dotenv

# .envファイルから設定を読み込む
load_dotenv()

# ボットのインスタンスとインテント設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ユーザーごとの会話履歴管理用
user_states = {}

# ランダムな会話リスト
talk_responses = [
    "こんにちは！今日はどうだった？",
    "元気だった？最近何か面白いことあった？",
    "お疲れ様～！今日はどんな感じだったかな？",
    "やっほ！最近どうしてたの～？",
    "こんにちはっ！今日も元気にいこうね！"
]

# 会話履歴から次の言葉をマルコフ連鎖で生成
def generate_response_from_history(user_id):
    conversation_history = get_user_state(user_id)['conversation']
    if len(conversation_history) < 2:
        return random.choice(talk_responses)

    # マルコフ連鎖風に次の単語を生成
    last_message = conversation_history[-1]
    if "元気" in last_message:
        return "えへへ、元気だよ～！"
    elif "お疲れ様" in last_message:
        return "ありがとう！今日はちょっと疲れたけど元気だよ～！"
    else:
        return random.choice(talk_responses)

# ユーザーの会話履歴更新
def update_user_state(user_id, message):
    if user_id not in user_states:
        user_states[user_id] = {'conversation': []}
    user_states[user_id]['conversation'].append(message)

# ユーザーの会話履歴取得
def get_user_state(user_id):
    return user_states.get(user_id, {'conversation': []})

# メスガキ口調の管理
user_styles = {}

# メスガキコマンド
@bot.command(name="mesugaki")
async def mesugaki(ctx):
    user_styles[ctx.author.id] = "mesugaki"
    await ctx.send(f"{ctx.author.name}はメスガキ口調になったにゃん！")

# リセットコマンド
@bot.command(name="reset")
async def reset(ctx):
    if ctx.author.id in user_styles:
        del user_styles[ctx.author.id]
    await ctx.send(f"{ctx.author.name}の口調が元に戻ったにゃん！")

# ボットがメンションされた時の会話処理
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id
    update_user_state(user_id, message.content)

    # メスガキ口調に変更
    if user_id in user_styles and user_styles[user_id] == "mesugaki":
        response = "うるさいにゃん！こっち来いよ、早くにゃ！"
    else:
        response = generate_response_from_history(user_id)

    await message.channel.send(response)

# ダイスロールコマンド
@bot.command(name="dice")
async def dice(ctx, dice_input: str):
    try:
        num_dice, dice_sides = map(int, dice_input.split('d'))
        rolls = [random.randint(1, dice_sides) for _ in range(num_dice)]
        total = sum(rolls)
        roll_result = ', '.join(map(str, rolls))
        await ctx.send(f"ロール結果は：{roll_result} (合計: {total}) だよ～！")
    except ValueError:
        await ctx.send("うーん、入力形式が違うみたい。「2d6」みたいに入力してね！")

# じゃんけん（ボタン選択）
@bot.command(name="janken")
async def janken(ctx):
    buttons = [
        discord.ui.Button(label="グー", custom_id="rock"),
        discord.ui.Button(label="チョキ", custom_id="scissors"),
        discord.ui.Button(label="パー", custom_id="paper")
    ]
    view = discord.ui.View()
    for button in buttons:
        view.add_item(button)

    await ctx.send("じゃんけんをしよう！選んでね～", view=view)

# じゃんけん結果処理
@bot.event
async def on_button_click(interaction):
    if interaction.user.bot:
        return

    user_hand = interaction.custom_id
    hands = ["グー", "チョキ", "パー"]
    bot_hand = random.choice(hands)

    results = {
        ("グー", "チョキ"): "あなたの勝ち～！やったね！",
        ("チョキ", "パー"): "あなたの勝ち～！すごいね！",
        ("パー", "グー"): "あなたの勝ち～！おめでとう！",
        ("チョキ", "グー"): "あなたの負けだよ～。また挑戦してね！",
        ("パー", "チョキ"): "あなたの負けだよ～。次頑張ろうね！",
        ("グー", "パー"): "あなたの負けだよ～。次はどうかな〜？"
    }

    result = results.get((user_hand, bot_hand), "あいこだね～！")
    await interaction.response.send_message(f"あなた: {user_hand} - ボット: {bot_hand}\n結果: {result}")

# ヘルプ（コマンド一覧）
@bot.command(name="help")
async def help(ctx):
    help_text = """
    コマンド一覧:
    - !dice <n>d<m>: n個のm面のダイスを振る
    - !janken: じゃんけんをする
    - !help: コマンド一覧を表示
    - !mesugaki: メスガキ口調になる
    - !reset: 口調を元に戻す
    """
    await ctx.send(help_text)

# ボット起動
bot.run(os.getenv("DISCORD_TOKEN"))
