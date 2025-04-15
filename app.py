from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request, render_template
import os
from dotenv import load_dotenv
load_dotenv()

app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"]
)

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

# Slackのイベントエンドポイント
@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

# フロントページ
@flask_app.route("/")
def index():
    return render_template("index.html")

# Slackメンションに反応
@app.event("app_mention")
def handle_mention(event, say):
    user = event["user"]
    say(f"<@{user}> さん、呼びましたか？🤖")

if __name__ == "__main__":
    flask_app.run(port=3000)
