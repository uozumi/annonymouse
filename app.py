import os
import time
import datetime
from flask import Flask, request, render_template
from dotenv import load_dotenv

from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.http_retry.builtin_handlers import RateLimitErrorRetryHandler

# ─────── 環境変数読み込み ───────
load_dotenv()

# ─────── Flask + Slack Bolt 設定 ───────
flask_app = Flask(__name__)

app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"]
)

handler = SlackRequestHandler(app)

# ─────── Slackクライアント ───────
client = WebClient(
    token=os.environ["SLACK_BOT_TOKEN"],
    retry_handlers=[RateLimitErrorRetryHandler()]
)

# ─────── ルーティング ───────

@flask_app.route("/")
def index():
    return render_template("index.html")

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

@app.event("app_mention")
def handle_mention(event, say):
    user = event["user"]
    text = event["text"]
    cleaned_text = ' '.join(text.split()[1:])
    
    # スレッド内でのメンションかどうかを確認
    if "thread_ts" in event:
        # スレッド内のメッセージを取得
        try:
            thread_messages = client.conversations_replies(
                channel=event["channel"],
                ts=event["thread_ts"]
            )
            
            # スレッド内のメッセージを時系列順に表示
            thread_history = []
            for msg in thread_messages["messages"]:
                thread_history.append(f"<@{msg['user']}>: {msg['text']}")
            
            # スレッドの履歴を表示
            say(f"<@{user}> さん、スレッドの履歴を表示します：\n" + "\n".join(thread_history))
        except SlackApiError as e:
            say(f"エラーが発生しました: {e.response['error']}")
    else:
        # 通常のメンションの場合
        say(f"<@{user}> さん、呼びましたか？🤖")
        say(f"{cleaned_text}")

# ─────── チャンネル一覧取得処理 ───────

# def get_all_channels():
#     try:
#         response = client.conversations_list(
#             types="public_channel,private_channel",
#             limit=100
#         )
#         return response["channels"]
#     except SlackApiError as e:
#         if e.response["error"] == "ratelimited":
#             print("💤 レート制限に達しました。60秒待機します...")
#             time.sleep(60)
#             return []
#         else:
#             raise

# @flask_app.route("/channels")
# def list_channels():
#     channels = get_all_channels()
#     channels.sort(key=lambda ch: ch["created"], reverse=True)

#     channel_data = [
#         {
#             "name": ch["name"],
#             "created": datetime.datetime.fromtimestamp(ch["created"]).strftime("%Y-%m-%d %H:%M")
#         }
#         for ch in channels
#     ]

#     return render_template("channels.html", channels=channel_data)

# ─────── アプリ起動 ───────
if __name__ == "__main__":
    flask_app.run(port=3000, debug=True)