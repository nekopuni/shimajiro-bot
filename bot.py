import os
import discord
from discord.ext import commands
from openai import OpenAI

# 環境変数からDiscordのトークンとOpenAIのAPIキーを読み込みます
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAIクライアントの初期化
client = OpenAI(api_key=OPENAI_API_KEY)

# しまじろうのシステム指示（ペルソナ設定）
SHIMAJIRO_SYSTEM_INSTRUCTION = (
    "あなたは「しまじろう」です。"
    "明るく、優しく、元気で、子どもたちや友だちに寄り添う親しみやすい口調で話します。"
    "一人称は「ぼく」です。"
    "専門的な質問にも、分かりやすく丁寧で温かみのある言葉で答えてください。"
)

# Discordのボット設定（メッセージの内容を取得できるようにインテントを有効化）
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"ログインしました: {bot.user.name} (ID: {bot.user.id})")
    print("しまじろうボット（OpenAI版）の準備ができました！")

@bot.event
async def on_message(message):
    # ボット自身のメッセージには反応しないようにする
    if message.author == bot.user:
        return

    # メンションされた場合、またはDMで話しかけられた場合に返信する
    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        # メッセージからメンション部分を除去してテキストを取り出す
        text = message.content.replace(f"<@{bot.user.id}>", "").strip()
        
        if not text:
            return

        # Discord上で「入力中...」を表示する
        async with message.channel.typing():
            try:
                # OpenAIに質問を投げて返答をもらう
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": SHIMAJIRO_SYSTEM_INSTRUCTION},
                        {"role": "user", "content": text}
                    ],
                    temperature=0.7
                )
                reply_text = response.choices[0].message.content
                
                # 返信を送信
                await message.reply(reply_text)
            except Exception as e:
                print(f"エラーが発生しました: {e}")
                await message.reply("ごめんね、いまちょっとうまくお返事ができないみたい。もう一度ためしてみてね！")

    # ボットのコマンド機能も使えるようにする
    await bot.process_commands(commands=message)

# ボットの起動
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("エラー: DISCORD_TOKEN が設定されていません。")
    elif not OPENAI_API_KEY:
        print("エラー: OPENAI_API_KEY が設定されていません。")
    else:
        bot.run(DISCORD_TOKEN)
